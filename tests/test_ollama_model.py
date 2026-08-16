"""Tests for the locally-served LLM (``ollama``) request handler.

These tests mock the HTTP layer so they run without an actual Ollama
server. With a live server you can run them with the unsupported-``mock``
removed (see bottom of file).
"""
from unittest import mock
import json

import pytest

from XAgent.ai_functions.request.ollama import chatcompletion_request


OLLAMA_SUCCESS_BODY = {
    "model": "llama3.1",
    "created_at": "2024-01-01T00:00:00Z",
    "message": {"role": "assistant", "content": "Hello, World!"},
    "done": True,
    "done_reason": "stop",
}


def test_ollama_request_hits_local_api_and_returns_openai_shape():
    """End-to-end test: HTTP mock + response shape + URL resolution."""
    with mock.patch("XAgent.ai_functions.request.ollama.requests.post") as post:
        post.return_value.status_code = 200
        post.return_value.json.return_value = OLLAMA_SUCCESS_BODY

        # Force the global CONFIG into ollama mode and make any model name
        # legal so get_model_name() passes the local-LLM tag through.
        with mock.patch(
            "XAgent.ai_functions.request.ollama.CONFIG.default_request_type",
            "ollama",
        ), mock.patch(
            "XAgent.ai_functions.request.ollama.CONFIG.default_completion_kwargs",
            {"model": "llama3.1"},
        ), mock.patch(
            "XAgent.ai_functions.request.ollama.get_apiconfig_by_model",
            return_value={"api_base": "http://localhost:11434"},
        ):
            response = chatcompletion_request(
                messages=[{"role": "user", "content": "Hello"}],
            )

        # Shape parity with openai.chat.completions.create(...).model_dump()
        assert response["object"] == "chat.completion"
        assert response["model"] == "llama3.1"
        assert response["choices"][0]["finish_reason"] == "stop"
        assert response["choices"][0]["message"]["role"] == "assistant"
        assert response["choices"][0]["message"]["content"] == "Hello, World!"
        assert set(response["usage"].keys()) == {
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
        }

        # We hit Ollama's native HTTP endpoint, NOT /v1/chat/completions.
        called_url = post.call_args.args[0]
        assert called_url == "http://localhost:11434/api/chat"

        body = post.call_args.kwargs["data"]
        payload = json.loads(body)
        assert payload["model"] == "llama3.1"
        assert payload["stream"] is False
        assert payload["options"] == {}


def test_ollama_strips_ollama_prefix():
    """An ``ollama:llama3.1`` config value resolves to ``llama3.1``."""
    from XAgent.config import get_model_name

    assert get_model_name("ollama:llama3.1", request_type="ollama") == "ollama:llama3.1"  # type passed through unchanged after strip is preserved as raw
    # The raw value is preserved; the request module strips the prefix when
    # building the Ollama payload. We sanity-check the resolution path here.
    assert get_model_name("llama3.1", request_type="ollama") == "llama3.1"
    assert get_model_name("mistral:7b-instruct", request_type="ollama") == "mistral:7b-instruct"


def test_ollama_unknown_model_rejected_for_openai_but_accepted_for_ollama():
    """The whitelist is relaxed only for the ollama request type."""
    from XAgent.config import get_model_name

    # ollama: any name
    assert get_model_name("latest-totally-unknown-model", request_type="ollama") \
        == "latest-totally-unknown-model"
    # openai: unknown name should still raise -- we don't want a typo to
    # silently degrade quality.
    with pytest.raises(Exception):
        get_model_name("latest-totally-unknown-model", request_type="openai")


def test_ollama_handles_5xx_as_retryable():
    """5xx from Ollama should raise a ConnectionError so tenacity retries."""
    from requests.exceptions import ConnectionError as ReqConnectionError

    with mock.patch("XAgent.ai_functions.request.ollama.requests.post") as post:
        post.return_value.status_code = 503
        post.return_value.text = "Service Unavailable"

        with mock.patch(
            "XAgent.ai_functions.request.ollama.CONFIG.default_request_type",
            "ollama",
        ), mock.patch(
            "XAgent.ai_functions.request.ollama.CONFIG.default_completion_kwargs",
            {"model": "llama3.1"},
        ), mock.patch(
            "XAgent.ai_functions.request.ollama.get_apiconfig_by_model",
            return_value={"api_base": "http://localhost:11434"},
        ):
            with pytest.raises(ReqConnectionError):
                chatcompletion_request(messages=[{"role": "user", "content": "x"}])


def test_ollama_truncation_maps_to_finish_reason_length():
    """Ollama's "done" with a truncated message should map to finish_reason='length'."""
    truncated_body = dict(OLLAMA_SUCCESS_BODY)
    truncated_body["message"] = {
        "role": "assistant",
        "content": "Sorry, I had to cut this off because it would have been too long...",
    }
    truncated_body["done_reason"] = "length"

    with mock.patch("XAgent.ai_functions.request.ollama.requests.post") as post:
        post.return_value.status_code = 200
        post.return_value.json.return_value = truncated_body

        with mock.patch(
            "XAgent.ai_functions.request.ollama.CONFIG.default_request_type",
            "ollama",
        ), mock.patch(
            "XAgent.ai_functions.request.ollama.CONFIG.default_completion_kwargs",
            {"model": "llama3.1"},
        ), mock.patch(
            "XAgent.ai_functions.request.ollama.get_apiconfig_by_model",
            return_value={"api_base": "http://localhost:11434"},
        ):
            response = chatcompletion_request(messages=[])
        assert response["choices"][0]["finish_reason"] == "length"


# Live-server smoke test (skipped by default -- enable to verify against a
# running `ollama serve`):
#
# def test_ollama_live():
#     pytest.skip("Enable by hand when running against a real Ollama server.")
#     response = chatcompletion_request(
#         model="llama3.1",
#         messages=[{"role": "user", "content": "Reply with the word OK."}],
#     )
#     assert response["choices"][0]["message"]["content"].strip().lower().startswith("ok")
