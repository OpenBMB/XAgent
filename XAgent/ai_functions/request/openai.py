import json
from XAgent.logs import logger
from XAgent.config import CONFIG, get_apiconfig_by_model, get_model_name
import pkg_resources


def chat_completion_to_dict(chat_completion_instance):
    choices = chat_completion_instance.choices[0]
    finish_reason = choices.finish_reason
    index = choices.index

    if choices.message.function_call:
        function_call = {
            "name": choices.message.function_call.name,
            "arguments": choices.message.function_call.arguments,
        }
    else:
        function_call = None

    if choices.message.tool_calls:
        tool_calls = {
            "id": choices.message.tool_calls.id,
            "type": choices.message.tool_calls.type,
            "function": {
                "name": choices.message.tool_calls.function_call.name,
                "arguments": choices.message.tool_calls.function_call.arguments,
            },
        }
    else:
        tool_calls = None

    message = {
        "content": choices.message.content,
        "role": choices.message.role,
        "function_call": function_call,
        "tool_calls": tool_calls,
    }
    content_filter_results = choices.content_filter_results
    choices_list = [
        {
            "index": index,
            "finish_reason": finish_reason,
            "message": message,
            "content_filter_results": content_filter_results,
        }
    ]
    response = {
        "id": chat_completion_instance.id,
        "choices": choices_list,
        "created": chat_completion_instance.created,
        "model": chat_completion_instance.model,
        "system_fingerprint": chat_completion_instance.system_fingerprint,
        "usage": {
            "completion_tokens": chat_completion_instance.usage.completion_tokens,
            "prompt_tokens": chat_completion_instance.usage.prompt_tokens,
            "total_tokens": chat_completion_instance.usage.total_tokens,
        },
        "object": "chat.completion",
    }
    return response


def handle_max_context_length_error(
    model_name, chatcompletion_kwargs, kwargs, openai_function
):
    if model_name == "gpt-4" and "gpt-4-32k" in CONFIG.api_keys:
        model_name = "gpt-4-32k"
    else:
        model_name = "gpt-3.5-turbo-16k"

    print(f"max context length reached, retrying with {model_name}")
    chatcompletion_kwargs = get_apiconfig_by_model(model_name)
    chatcompletion_kwargs.update(kwargs)
    chatcompletion_kwargs.pop("schema_error_retry", None)

    response = openai_function(**chatcompletion_kwargs)
    return response


def chatcompletion_request(**kwargs):
    model_name = get_model_name(
        kwargs.pop("model", CONFIG.default_completion_kwargs["model"])
    )
    logger.debug("chatcompletion: using " + model_name)
    chatcompletion_kwargs = get_apiconfig_by_model(model_name)

    if pkg_resources.parse_version(
        pkg_resources.get_distribution("openai").version
    ) >= pkg_resources.parse_version("1.0.0"):
        from openai import OpenAI, BadRequestError

        request_timeout = kwargs.pop("request_timeout", 60)
        if "base_url" in chatcompletion_kwargs:
            base_url = chatcompletion_kwargs.pop("base_url", None)
        elif "api_base" in chatcompletion_kwargs:
            base_url = chatcompletion_kwargs.pop("api_base", None)
        api_key = chatcompletion_kwargs.pop("api_key", None)
        chatcompletion_kwargs.update(kwargs)
        client = OpenAI(api_key=api_key, base_url=base_url)
        print()
        try:
            response = chat_completion_to_dict(
                client.chat.completions.create(**chatcompletion_kwargs)
            )
            if response["choices"][0]["finish_reason"] == "length":
                raise BadRequestError("maximum context length exceeded", None)
        except BadRequestError as e:
            if "maximum context length" in e._message:
                response = handle_max_context_length_error(
                    model_name,
                    chatcompletion_kwargs,
                    kwargs,
                    client.chat.completions.create,
                )
            else:
                raise e

    else:
        import openai
        from openai.error import InvalidRequestError

        chatcompletion_kwargs.update(kwargs)

        try:
            response = openai.ChatCompletion.create(**chatcompletion_kwargs)
            response = json.loads(str(response))
            if response["choices"][0]["finish_reason"] == "length":
                raise InvalidRequestError("maximum context length exceeded", None)
        except InvalidRequestError as e:
            if "maximum context length" in e._message:
                response = handle_max_context_length_error(
                    model_name,
                    chatcompletion_kwargs,
                    kwargs,
                    openai.ChatCompletion.create,
                )
            else:
                raise e

    return response
