"""Request handler for locally-deployed LLMs (focus: Ollama).

This module exposes ``chatcompletion_request`` with the same call signature as
``XAgent.ai_functions.request.openai`` so the rest of XAgent (``OBJGenerator``,
``FunctionManager``, ``BaseAgent``, ``FunctionHandler``) does not need to learn a
new schema to talk to a local model server.

Strategy
--------
We hit Ollama's native HTTP API at ``<api_base>/api/chat`` (default
``http://localhost:11434/api/chat``). We translate the response into the same
dictionary shape produced by ``openai.OpenAI(...).chat.completions.create(...).
model_dump()``:

.. code-block:: python

    {
        "id": "ollama-<model>",
        "model": "<model>",
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

This means callers (which currently destructure ``response["choices"][0]
["message"]["function_call"]`` and ``response["usage"]``) keep working
unchanged.  Tool / function-call flows that need schema-validated JSON should
point Ollama's OpenAI-compatible endpoint (``/v1/chat/completions``) at the
existing ``openai`` request type instead -- see ``assets/ollama_config.yml``.

Why not just reuse ``openai.py``?
---------------------------------
Ollama's ``/v1/chat/completions`` is OpenAI-shaped but its tool/function
support and ``finish_reason`` semantics are not 1:1 with OpenAI's.  By
talking to ``/api/chat`` directly we keep a single, stable contract for the
common case (plain chat) and we avoid pulling the ``openai`` SDK for the
"self-hosted" path.

Token counts
------------
Ollama's ``/api/chat`` reports prompt and eval durations but no token counts.
We approximate tokens from the raw text using tiktoken's ``cl100k_base``
encoding -- an estimate that is good enough for XAgent's prompt accounting
(``XAgent.utils.get_token_nums`` already uses the same encoding for unknown
models).
"""
from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, List, Optional

import requests
import tiktoken
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_chain,
    wait_exponential,
    wait_none,
)

from XAgent.config import CONFIG, get_apiconfig_by_model, get_model_name
from XAgent.logs import logger


# Ollama's local HTTP default. Same default Ollama itself prints when started.
DEFAULT_OLLAMA_API_BASE = "http://localhost:11434"

# JSON-ish status codes we treat as retryable. We are conservative: anything
# that looks like a transient connection or 5xx is worth retrying; 4xx is not.
RETRY_ERRORS: tuple = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)


# Reused across calls. ``cl100k_base`` is what every modern OpenAI model uses
# and it is what ``XAgent.utils`` falls back to for unknown models, so the
# prompt-side accounting stays consistent.
_ENCODING = tiktoken.get_encoding("cl100k_base")


def _approximate_tokens(text: str) -> int:
    """Roughly count tokens. Used only for the ``usage`` field."""
    if not text:
        return 0
    try:
        return len(_ENCODING.encode(text))
    except Exception:  # pragma: no cover - tiktoken never raises on str
        # Character-based fallback if tiktoken is broken / stripped.
        return max(1, len(text) // 4)


def _to_openai_shape(
    model: str,
    content: str,
    prompt_messages: List[Dict[str, Any]],
    finish_reason: str = "stop",
    response_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Translate an Ollama ``/api/chat`` response into OpenAI shape."""
    prompt_tokens = sum(_approximate_tokens(m.get("content") or "") for m in prompt_messages)
    completion_tokens = _approximate_tokens(content)
    return {
        "id": response_id or f"ollama-chat-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "finish_reason": finish_reason,
                "message": {"role": "assistant", "content": content},
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


@retry(
    retry=retry_if_exception_type(RETRY_ERRORS),
    stop=stop_after_attempt(CONFIG.max_retry_times + 3),
    wait=wait_chain(
        *[wait_none() for _ in range(3)] + [wait_exponential(min=4, max=60)]
    ),
    reraise=True,
)
def chatcompletion_request(**kwargs) -> Dict[str, Any]:
    """Issue a chat completion to a local Ollama server.

    Args:
        **kwargs: Any kwarg accepted by the OpenAI ``chat.completions.create``
            method.  Recognised keys here are: ``model``, ``messages``,
            ``temperature``, ``top_p``, ``max_tokens``, ``stop``, ``api_base``,
            ``request_timeout``.  Unknown keys are passed through to Ollama as
            part of the ``options`` payload (Ollama merges anything in
            ``options``).

    Returns:
        dict: Response shaped like OpenAI's ``chat.completion`` object.

    Raises:
        BadRequestError-equivalent dict on a non-retryable error
        (``BadRequestError`` is re-exported below for parity with the openai
        request module).
    """
    # Resolve the model name.  ``get_model_name`` returns the input unchanged
    # for the ``ollama`` request type, which is exactly what we want: Ollama
    # models are referenced by their tag (e.g. ``llama3.1:8b-instruct-q5_K_M``).
    model_name = get_model_name(
        kwargs.pop("model", CONFIG.default_completion_kwargs["model"]),
        request_type=CONFIG.default_request_type,
    )
    logger.debug("ollama chatcompletion: using " + model_name)

    chatcompletion_kwargs = get_apiconfig_by_model(model_name)

    # Allow call-site override (``objgenerator.chatcompletion`` does not
    # forward ``api_base`` directly).
    api_base_override = kwargs.pop("api_base", None)
    request_timeout = kwargs.pop("request_timeout", 60)

    default_api_base = chatcompletion_kwargs.get("api_base") or DEFAULT_OLLAMA_API_BASE
    api_base = api_base_override or default_api_base
    # Ollama's chat endpoint is fixed; strip trailing slashes and any path the
    # user pasted so we always POST to <host>/api/chat.
    api_base = api_base.rstrip("/")
    if api_base.endswith("/api/chat"):
        chat_url = api_base
    elif api_base.endswith("/v1"):
        chat_url = api_base.rsplit("/v1", 1)[0] + "/api/chat"
    else:
        chat_url = api_base + "/api/chat"

    messages: List[Dict[str, Any]] = kwargs.pop("messages", []) or []

    # Everything that isn't a top-level Ollama field goes into ``options``.
    options: Dict[str, Any] = {}
    for key in (
        "temperature",
        "top_p",
        "top_k",
        "num_predict",
        "max_tokens",
        "stop",
        "seed",
        "repeat_penalty",
        "repetition_penalty",
        "frequency_penalty",
        "presence_penalty",
        "mirostat",
        "mirostat_eta",
        "mirostat_tau",
        "num_ctx",
    ):
        if key in chatcompletion_kwargs:
            options[key] = chatcompletion_kwargs[key]
        if key in kwargs:
            options[key] = kwargs.pop(key)

    # ``max_tokens`` -> ``num_predict`` is Ollama's name.
    if "max_tokens" in options and "num_predict" not in options:
        options["num_predict"] = options.pop("max_tokens")

    payload: Dict[str, Any] = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": options,
    }
    # Optional JSON-mode (Ollama >= 0.5). Forwarded if explicitly requested.
    json_mode = kwargs.pop("json_mode", False) or chatcompletion_kwargs.get(
        "format"
    ) == "json"
    if json_mode:
        payload["format"] = "json"

    logger.debug(f"ollama POST {chat_url} (model={model_name}, "
                 f"messages={len(messages)})")

    try:
        http_response = requests.post(
            chat_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=request_timeout,
        )
    except requests.exceptions.RequestException as exc:
        # tenacity will retry on the ones we listed in RETRY_ERRORS; anything
        # else bubbles up with a more helpful message.
        raise RuntimeError(
            f"Cannot reach local Ollama at {chat_url}: {exc}. "
            "Is `ollama serve` running and reachable?"
        ) from exc

    if http_response.status_code >= 500:
        # Retryable on the server side.
        raise requests.exceptions.ConnectionError(
            f"Ollama returned HTTP {http_response.status_code}: "
            f"{http_response.text[:200]}"
        )

    if http_response.status_code >= 400:
        # 4xx is the user's fault -- do not retry.
        raise RuntimeError(
            f"Ollama rejected the request (HTTP {http_response.status_code}): "
            f"{http_response.text[:500]}"
        )

    try:
        data = http_response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Ollama returned a non-JSON body: {http_response.text[:200]}"
        ) from exc

    # ``/api/chat`` (non-streaming) returns:
    #   {"model": "...", "created_at": "...", "message": {"role": "assistant",
    #    "content": "..."}, "done": true, ...}
    response_message = data.get("message") or {}
    content = response_message.get("content", "") or ""

    finish_reason = "stop"
    if data.get("done_reason") == "length":
        finish_reason = "length"
    # If Ollama hit the context limit (max_tokens / num_ctx) the response is
    # truncated; treat that like OpenAI's "length" reason so the rest of
    # XAgent can react correctly.
    if content.endswith("...") and data.get("done") is True:
        finish_reason = "length"

    return _to_openai_shape(
        model=model_name,
        content=content,
        prompt_messages=messages,
        finish_reason=finish_reason,
        response_id=data.get("id"),
    )


# Re-export a couple of names callers may want for switching behavior.
__all__ = ["chatcompletion_request", "DEFAULT_OLLAMA_API_BASE"]
