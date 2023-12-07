import json
import openai
from XAgent.logs import logger
from XAgent.config import CONFIG, get_apiconfig_by_model, get_model_name

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_not_exception_type,
    wait_chain,
    wait_none,
)
import importlib.metadata as metadata

if metadata.version("openai") < "1.0":
    from openai.error import AuthenticationError, PermissionError, InvalidRequestError

    RETRY_ERRORS = (
        AuthenticationError,
        PermissionError,
        InvalidRequestError,
        AssertionError,
    )

    @retry(
        retry=retry_if_not_exception_type(RETRY_ERRORS),
        stop=stop_after_attempt(CONFIG.max_retry_times + 3),
        wait=wait_chain(
            *[wait_none() for _ in range(3)] + [wait_exponential(min=61, max=293)]
        ),
        reraise=True,
    )
    def chatcompletion_request(**kwargs):
        """Handle operation of OpenAI chat completion.

        This function operates OpenAI chat completion with provided
        arguments. It gets the model name, applies a JSON web token, if the
        response indicates the context length has been exceeded, it attempts
        to get a higher-capacity language model if it exists in the configuration
        and reattempts the operation. Otherwise, it will raise an error message.

        Args:
            **kwargs: Variable length argument list including (model:str, etc.).

        Returns:
            dict: chat completion response.

        Raises:
            InvalidRequestError: If any error occurs during chat completion operation or
            context length limit exceeded and no fallback models available.
        """
        model_name = get_model_name(
            kwargs.pop("model", CONFIG.default_completion_kwargs["model"])
        )
        logger.debug("chatcompletion: using " + model_name)
        chatcompletion_kwargs = get_apiconfig_by_model(model_name)
        if "azure_endpoint" in chatcompletion_kwargs:
            api_base = chatcompletion_kwargs.pop("azure_endpoint", None)
            chatcompletion_kwargs.update({"api_base": api_base})
        chatcompletion_kwargs.update(kwargs)

        try:
            response = openai.ChatCompletion.create(**chatcompletion_kwargs)
            response = json.loads(str(response))
            if response["choices"][0]["finish_reason"] == "length":
                raise InvalidRequestError("maximum context length exceeded", None)
        except InvalidRequestError as e:
            if "maximum context length" in e._message:
                if model_name == "gpt-4":
                    if "gpt-4-32k" in CONFIG.api_keys:
                        model_name = "gpt-4-32k"
                    elif "gpt-4-1106-preview" in CONFIG.api_keys:
                        model_name = "gpt-4-1106-preview"
                    else:
                        model_name = "gpt-3.5-turbo-16k"
                elif model_name == "gpt-3.5-turbo":
                    if "gpt-3.5-turbo-1106" in CONFIG.api_keys:
                        model_name = "gpt-3.5-turbo-1106"
                    else:
                        model_name = "gpt-3.5-turbo-16k"
                else:
                    raise e
                print("max context length reached, retrying with " + model_name)
                chatcompletion_kwargs = get_apiconfig_by_model(model_name)
                chatcompletion_kwargs.update(kwargs)
                chatcompletion_kwargs.pop("schema_error_retry", None)

                response = openai.ChatCompletion.create(**chatcompletion_kwargs)
                response = json.loads(str(response))
            else:
                raise e

        return response

else:
    from openai import AuthenticationError, PermissionDeniedError, BadRequestError

    RETRY_ERRORS = (
        AuthenticationError,
        PermissionDeniedError,
        BadRequestError,
        AssertionError,
    )

    @retry(
        retry=retry_if_not_exception_type(RETRY_ERRORS),
        stop=stop_after_attempt(CONFIG.max_retry_times + 3),
        wait=wait_chain(
            *[wait_none() for _ in range(3)] + [wait_exponential(min=61, max=293)]
        ),
        reraise=True,
    )
    def chatcompletion_request(**kwargs):
        """Handle operation of OpenAI v1.x.x chat completion.

        This function operates OpenAI v1.x.x chat completion with provided
        arguments. It gets the model name, applies a JSON web token, if the
        response indicates the context length has been exceeded, it attempts
        to get a higher-capacity language model if it exists in the configuration
        and reattempts the operation. Otherwise, it will raise an error message.

        Args:
            **kwargs: Variable length argument list including (model:str, etc.).

        Returns:
            response (dict): A dictionary containing the response from the Chat API.
            The structure of the dictionary is based on the API response format.

        Raises:
            BadRequestError: If any error occurs during chat completion operation or
            context length limit exceeded and no fallback models available.
        """
        model_name = get_model_name(
            kwargs.pop("model", CONFIG.default_completion_kwargs["model"])
        )
        logger.debug("chatcompletion: using " + model_name)
        chatcompletion_kwargs = get_apiconfig_by_model(model_name)

        request_timeout = kwargs.pop("request_timeout", 60)
        if "api_version" in chatcompletion_kwargs:
            if "base_url" in chatcompletion_kwargs:
                base_url = chatcompletion_kwargs.pop("base_url", None)
            else:
                base_url = chatcompletion_kwargs.pop("api_base", None)
            azure_endpoint = chatcompletion_kwargs.pop("azure_endpoint", base_url)
            api_version = chatcompletion_kwargs.pop("api_version", None)
            api_key = chatcompletion_kwargs.pop("api_key", None)
            chatcompletion_kwargs.pop("api_type", None)
            if "engine" in chatcompletion_kwargs:
                model = chatcompletion_kwargs.pop("engine", None)
            else:
                model = chatcompletion_kwargs.pop("model", None)
            chatcompletion_kwargs.update({"model": model})
            chatcompletion_kwargs.update(kwargs)
            client = openai.AzureOpenAI(
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                timeout=request_timeout,
            )
        else:
            if "base_url" in chatcompletion_kwargs:
                base_url = chatcompletion_kwargs.pop("base_url", None)
            else:
                base_url = chatcompletion_kwargs.pop("api_base", None)
            api_key = chatcompletion_kwargs.pop("api_key", None)
            organization = chatcompletion_kwargs.pop("organization", None)
            chatcompletion_kwargs.update(kwargs)
            client = openai.OpenAI(
                api_key=api_key,
                organization=organization,
                base_url=base_url,
                timeout=request_timeout
            )
        try:
            completions = client.chat.completions.create(**chatcompletion_kwargs)
            response = completions.model_dump()
            if response["choices"][0]["finish_reason"] == "length":
                raise BadRequestError(
                    message="maximum context length exceeded", response=None, body=None
                )

        except BadRequestError as e:
            if "maximum context length" in e.message:
                if model_name == "gpt-4" and "gpt-4-32k" in CONFIG.api_keys:
                    model_name = "gpt-4-32k"
                elif model_name == "gpt-4" and "gpt-4-1106-preview" in CONFIG.api_keys:
                    model_name = "gpt-4-1106-preview"
                else:
                    if "gpt-3.5-turbo-1106" in CONFIG.api_keys:
                        model_name = "gpt-3.5-turbo-1106"
                    else:
                        model_name = "gpt-3.5-turbo-16k"

                print(f"max context length reached, retrying with {model_name}")
                chatcompletion_kwargs = get_apiconfig_by_model(model_name)
                request_timeout = kwargs.pop("request_timeout", 60)
                if "base_url" in chatcompletion_kwargs:
                    base_url = chatcompletion_kwargs.pop("base_url", None)
                else:
                    base_url = chatcompletion_kwargs.pop("api_base", None)
                api_key = chatcompletion_kwargs.pop("api_key", None)
                chatcompletion_kwargs.update(kwargs)
                chatcompletion_kwargs.pop("schema_error_retry", None)
                completions = client.chat.completions.create(**chatcompletion_kwargs)
                response = completions.model_dump()
            else:
                raise e

        return response


