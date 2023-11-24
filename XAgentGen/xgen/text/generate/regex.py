from typing import TYPE_CHECKING, Dict, List, Optional, Set, Union

import interegular

from cachetools import TTLCache
from outlines.text.generate.regex import Regex
from outlines.text.fsm import create_fsm_index_tokenizer, make_deterministic_fsm

if TYPE_CHECKING:
    from outlines.text.generate.sample import Sampler


pstate_to_vocab_path_cache = TTLCache(maxsize=20, ttl=3600)

def to_hash(vocabulary, regex_str, eos_token):
    string = f"vocabulary:{''.join(vocabulary)}, regex: {regex_str}, eos_token: {eos_token}"
    return hash(string)

class XRegex(Regex):
    def __init__(
        self,
        model,
        regex_string: str,
        max_tokens: Optional[int] = None,
        *,
        sampler: Optional["Sampler"] = None,
        stop: Union[str, List[str]] = [],
        allow_empty_tokens: bool = True,
        initial_state: Optional[int] = None,
        final_states: Optional[Set[int]] = None,
        states_to_token_maps: Optional[Dict[int, Dict[int, int]]] = None,
        empty_token_ids: Optional[Set[int]] = None,
    ):
        
        vocab = model.tokenizer.vocabulary
        sorted_vocabulary = [
            model.tokenizer.convert_token_to_string(k)
            for k, v in sorted(vocab.items(), key=lambda kv: kv[1])
        ]
        hash_key = to_hash(list(sorted_vocabulary), regex_string, model.tokenizer.eos_token)

        if hash_key in pstate_to_vocab_path_cache:
            regex_fsm,states_to_token_maps,empty_token_ids = pstate_to_vocab_path_cache[hash_key]
            initial_state = regex_fsm.initial
            final_states = regex_fsm.finals
        else:
            regex_pattern = interegular.parse_pattern(regex_string)
            regex_fsm, _ = make_deterministic_fsm(regex_pattern.to_fsm().reduce())
            (
                states_to_token_maps,
                empty_token_ids,
            ) = create_fsm_index_tokenizer(regex_fsm, model.tokenizer)
            initial_state = regex_fsm.initial
            final_states = regex_fsm.finals
            
            pstate_to_vocab_path_cache[hash_key] = (regex_fsm,states_to_token_maps,empty_token_ids)

        super().__init__(
            model, regex_string, max_tokens, sampler=sampler,stop=stop,
            allow_empty_tokens=allow_empty_tokens,initial_state=initial_state,final_states=final_states,
            states_to_token_maps=states_to_token_maps,empty_token_ids=empty_token_ids)

def multi_regex(
    model,
    choices: List[str],
    max_tokens: Optional[int] = None,
    *,
    sampler: Optional["Sampler"] = None,
    allow_empty_tokens: bool = True,
):
    regex_str = r"(" + r"|".join(choices) + r")"
    return XRegex(
        model,
        regex_str,
        max_tokens,
        sampler=sampler,
        allow_empty_tokens=allow_empty_tokens,
    )
