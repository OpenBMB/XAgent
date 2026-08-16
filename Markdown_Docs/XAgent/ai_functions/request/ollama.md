# `XAgent.ai_functions.request.ollama`

Module: `XAgent/ai_functions/request/ollama.py`
Function: `chatcompletion_request(**kwargs) -> dict`

## What it does

Issues chat completions against a locally-deployed Ollama server using the
native HTTP API at `<api_base>/api/chat` (default
`http://localhost:11434/api/chat`) and returns a dict in the same shape as
`openai.OpenAI(...).chat.completions.create(...).model_dump()`:

```python
{
    "id": "<ollama>",
    "object": "chat.completion",
    "created": <unix-ts>,
    "model": "<llama3.1>",
    "choices": [{
        "index": 0,
        "finish_reason": "stop" | "length",
        "message": {"role": "assistant", "content": "..."},
    }],
    "usage": {
        "prompt_tokens": <int>,
        "completion_tokens": <int>,
        "total_tokens": <int>,
    },
}
```

This means the rest of XAgent (`OBJGenerator`, `FunctionManager`,
`BaseAgent`, `FunctionHandler`) does **not** need to learn a new schema to
talk to a local model server — every existing
`response["choices"][0]["message"]["function_call"]` and `response["usage"]`
read site keeps working unchanged.

## When to use it

- You are running Ollama locally (`ollama serve`) and have pulled a model
  (`ollama pull llama3.1`, `ollama pull qwen2`, …).
- You want XAgent to talk to a self-hosted OpenAI-compatible server
  (vLLM, LocalAI, llama.cpp's HTTP server, etc.) without an OpenAI API
  key.
- You are working offline or air-gapped.

## When NOT to use it

- You need schema'd tool/function calling with strict validation against
  a function schema. Use `default_request_type: openai` and point
  `api_base` at Ollama's OpenAI-compatible `/v1/chat/completions`
  (Ollama >= 0.1.14), which routes tool calls through the existing
  `FunctionManager` logic.
- You need reliable token counts. The token counts returned in `usage`
  are approximations using `tiktoken`'s `cl100k_base` encoding; Ollama's
  native API does not report real token usage.

## Configuration

In your YAML config (`CONFIG_FILE=assets/ollama_config.yml`):

```yaml
api_keys:
  llama3.1:
    - api_key: ollama
      api_base: http://localhost:11434
      model: llama3.1

default_request_type: ollama
default_completion_kwargs:
  model: llama3.1
  temperature: 0.2
  max_tokens: 2048
  num_ctx: 4096
```

Recognised kwargs (mapped into Ollama's `options` block):

- `temperature`, `top_p`, `top_k`, `seed`
- `max_tokens` -> translated to `options.num_predict`
- `stop`, `frequency_penalty`, `presence_penalty`
- `repeat_penalty` / `repetition_penalty`
- `mirostat`, `mirostat_eta`, `mirostat_tau`
- `num_ctx` (Ollama context window)
- `format: json` / `json_mode: True` -> top-level `format` field

Unknown kwargs are forwarded into `options` as-is so future Ollama
additions take effect without code changes.

## Model name resolution

`XAgent.config.get_model_name(model_name, request_type)` relaxes the
whitelist for the `ollama` request type:

- Any exact common local family (`llama3`, `llama3.1`, `mistral`,
  `qwen2`, `phi3`, `gemma`, `codellama`, `deepseek-coder`, `command-r`,
  …) is accepted.
- The `ollama:` prefix is stripped automatically
  (`ollama:llama3.1` → resolved name `llama3.1`; the raw prefix still
  surfaces in error messages so users see what they typed).
- Anything else passes through unchanged **only** when
  `default_request_type: ollama` is set. The openai/xagent paths still
  raise on unknown names so a typo doesn't silently degrade quality.

## Errors / retries

- HTTP 5xx → retry via tenacity up to
  `CONFIG.max_retry_times + 3` times, then raise.
- HTTP 4xx → raise immediately with the server-supplied message (do not
  retry; this is user error).
- Connection refused / timeout → retry, then raise with a clear "Is
  `ollama serve` running?" hint.
- JSON parse failure → raise with the offending body excerpt.
- `done_reason == "length"` → maps to
  `finish_reason == "length"` so the rest of XAgent can react.

## Token accounting

`XAgent/utils.py` was tightened so the module-import-time call to
`tiktoken.encoding_for_model(...)` no longer raises `KeyError` for
locally-served model tags. If the model's tokens cannot be resolved, the
code falls back to `cl100k_base`, then to a character-rule estimate, then
to `None`. `get_token_nums` and `clip_text` are defensive about `None`.
