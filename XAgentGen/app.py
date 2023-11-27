from xgen.parser import FunctionParser
from xgen.server.datamodel import *
from xgen.server.message_formater import format
import xgen.text.generate as generate
from xgen.models.transformers import XTransformers
from outlines.models.transformers import TransformersTokenizer
from vllm.sampling_params import LogitsProcessor
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.utils import random_uuid
from vllm import SamplingParams
from typing import List
import torch
from addict import Dict
import json
from fastapi import FastAPI, Response, status, Request
from fastapi.middleware.cors import CORSMiddleware
import argparse
import uvicorn
from transformers import AutoTokenizer


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = argparse.ArgumentParser()
parser.add_argument("--model-path", type=str, help="Path to the model")
parser.add_argument("--port", type=str, help="Port for server")
args = parser.parse_args()

model_path = args.model_path

engine_configs = AsyncEngineArgs(
    worker_use_ray=False,
    engine_use_ray=False,
    model=model_path,
    tokenizer=None,
    tokenizer_mode='auto',
    tensor_parallel_size=1,
    dtype='auto',
    quantization=None,
    revision=None,
    tokenizer_revision=None,
    seed=42,
    gpu_memory_utilization=0.9,
    swap_space=4,
    disable_log_requests=True,
    max_num_batched_tokens=16384,
    max_model_len=16384,
)
engine = AsyncLLMEngine.from_engine_args(engine_configs)

tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code='auto',
            tokenizer_revision=None)

print("loading model finished! Service start!")


class ConstrainedLogitsProcessor(LogitsProcessor):
    def __init__(self, extra_arguments, functions, function_call, tokenizer_path, device=None):
        if function_call is not None and len(function_call) == 0:
            function_call = None
        self.dp = FunctionParser()
        outline_tokenizer = TransformersTokenizer(tokenizer_path)
        fake_model = Dict()
        fake_model.device = device
        model = XTransformers(fake_model, outline_tokenizer)
        self.dp.create_all_functions_model(extra_arguments, functions, function_call)
        regex_list = self.dp.models_to_regex()
        self.generator = generate.multi_regex(model, regex_list)

    def __call__(self, generated_token_ids: List[int], logits: torch.Tensor) -> torch.Tensor:
        generated_token_ids = torch.LongTensor(generated_token_ids).view(1, -1).to(logits.device)
        masked_logits = self.generator.create_proposal(generated_token_ids, logits.view(1, -1))
        return masked_logits

@app.post("/chat/health", status_code=200)
async def health():
    return "ok"


@app.post("/chat/completions")
async def chat_function(response:Response,request: Request):
    global engine
    call_msg = await request.json()
    model_name = call_msg.get("model","")
    if model_name != "agentllama" and model_name != "xagentllm":
        return {"model": "", "choices": [{'message': {'content': f'bad model {model_name}'}, 'finish_reason': 'error', 'index': -1}]}
    messages = call_msg.get("messages",None)
    arguments = call_msg.get("arguments",None)
    functions = call_msg.get("functions",None)
    function_call = call_msg.get("function_call",None)
    task_prompt = format({
        "messages": messages,
        "arguments": arguments,
        "functions": functions,
        "function_call": function_call
    }, dump_method='json')
    processor = ConstrainedLogitsProcessor(arguments, functions, function_call, model_path, device='cuda')
    sampling_params = SamplingParams(
        temperature=call_msg.get("temperature", 0.8),
        top_p=call_msg.get("top_p", 1.0),
        frequency_penalty=call_msg.get("frequency_penalty",0.5),
        presence_penalty=call_msg.get("presence_penalty", 0.0),
        repetition_penalty=call_msg.get("repetition_penalty",1.2),
        max_tokens=call_msg.get("max_tokens", 4000),
        logits_processors=[processor]
    )
    # make request
    request_id = random_uuid()
    # tokenize prompt
    input_ids = tokenizer.encode(task_prompt, return_tensors="pt")
    prompt_tokens = input_ids.shape[1]  
    results_generator = engine.generate(task_prompt, sampling_params, request_id)
    final_output = None
    async for request_output in results_generator:
        if await request.is_disconnected():
            # Abort the request if the client disconnects.
            await engine.abort(request_id)
            return Response(status_code=499)
        final_output = request_output
    sequence = final_output.outputs[0].text
    # tokenizer output
    output_ids = tokenizer.encode(sequence, return_tensors="pt")
    completion_tokens = output_ids.shape[1]
    try:
        sequence = json.loads(sequence)
        if "extra_parameters" in sequence:
            sequence["arguments"] = sequence["extra_parameters"]
            sequence.pop("extra_parameters")
    except Exception as e:
        res = {"status": "fail","broken_json":sequence,"error_message":str(e)}
    else:
        res = {
            "status": "success",
            "function_res": sequence,
            "usage":{
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        }

    if res["status"] == "fail":
        response.status_code = 400
        return {"model": "", "choices": [{'message': {'content': json.dumps(res,ensure_ascii=False)}, 'finish_reason': 'error', 'index': -1}]}
    
    response_model = {
        'model': model_name,
        'usage': res["usage"],
        'choices':[
            {
                "message":{
                    "content": json.dumps(res["function_res"], ensure_ascii=False)
                },
                "finish_reason":"stop",
                "index":0,
            }
        ]
    }
    return response_model

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(args.port))