from transformers.generation.logits_process import (
    LogitsProcessorList,
    RepetitionPenaltyLogitsProcessor,
    TemperatureLogitsWarper,
    TopKLogitsWarper,
    TopPLogitsWarper,
)

from outlines.models.transformers import Transformers,TransformersTokenizer
from typing import TYPE_CHECKING, List, Optional, Tuple, Union
if TYPE_CHECKING:
    from transformers import PreTrainedModel, PreTrainedTokenizer

import torch
KVCacheType = Tuple[Tuple[torch.DoubleTensor, torch.DoubleTensor], ...]

def prepare_logits_processor(
    temperature: float, repetition_penalty: float, top_p: float, top_k: int
) -> LogitsProcessorList:
    """generate the logits processor with params"""
    processor_list = LogitsProcessorList()
    # TemperatureLogitsWarper doesn't accept 0.0, 1.0 makes it a no-op so we skip two cases.
    if temperature >= 1e-5 and temperature != 1.0:
        processor_list.append(TemperatureLogitsWarper(temperature))
    if repetition_penalty > 1.0:
        processor_list.append(RepetitionPenaltyLogitsProcessor(repetition_penalty))
    if 1e-8 <= top_p < 1.0:
        processor_list.append(TopPLogitsWarper(top_p))
    if top_k > 0:
        processor_list.append(TopKLogitsWarper(top_k))
    return processor_list

class XTransformers(Transformers):
    def __init__(
        self,
        model: "PreTrainedModel",
        tokenizer: "PreTrainedTokenizer",
    ):
        super().__init__(model,tokenizer)
        self.logits_processor=None
    
    def reset(self):
        self.tokenizer.prompt_tokens = 0
        self.tokenizer.completion_tokens = 0

    def add_logits_processor(self,generate_kwargs:dict={}):

        temperature = float(generate_kwargs.get("temperature", 1.0))
        repetition_penalty = float(generate_kwargs.get("repetition_penalty", 1.0))
        top_p = float(generate_kwargs.get("top_p", 1.0))
        top_k = int(generate_kwargs.get("top_k", -1))  # -1 means disable

        logits_processor = prepare_logits_processor(
            temperature, repetition_penalty, top_p, top_k
        )

        self.logits_processor = logits_processor

    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.LongTensor,
        past_key_values: Optional[Tuple] = None,
    ) -> Tuple[torch.FloatTensor, Optional[KVCacheType]]:
        
        next_token_logits, output_past_key_values = super().forward(input_ids,attention_mask,past_key_values)
        
        if self.logits_processor:
            next_token_logits = self.logits_processor(input_ids,next_token_logits)
       
        return next_token_logits, output_past_key_values
