import json
import openai

from XAgent.logs import logger
from XAgent.config import CONFIG, get_apiconfig_by_model, get_model_name

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_not_exception_type, wait_chain, wait_none
import pkg_resources
if pkg_resources.get_distribution("openai").version < "1.0":
    from openai.error import AuthenticationError, PermissionError, InvalidRequestError
    RETRY_ERRORS = (AuthenticationError, PermissionError,
                    InvalidRequestError, AssertionError)

    @retry(
        retry=retry_if_not_exception_type(RETRY_ERRORS),
        stop=stop_after_attempt(CONFIG.max_retry_times+3),
        wait=wait_chain(*[wait_none() for _ in range(3)] +
                        [wait_exponential(min=61, max=293)]),
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
        model_name = get_model_name(kwargs.pop(
            'model', CONFIG.default_completion_kwargs['model']))
        logger.debug("chatcompletion: using " + model_name)
        chatcompletion_kwargs = get_apiconfig_by_model(model_name)
        chatcompletion_kwargs.update(kwargs)

        try:
            response = openai.ChatCompletion.create(**chatcompletion_kwargs)
            response = json.loads(str(response))
            if response['choices'][0]['finish_reason'] == 'length':
                raise InvalidRequestError(
                    'maximum context length exceeded', None)
        except InvalidRequestError as e:
            if 'maximum context length' in e._message:
                if model_name == 'gpt-4':
                    if 'gpt-4-32k' in CONFIG.api_keys:
                        model_name = 'gpt-4-32k'
                    else:
                        model_name = 'gpt-3.5-turbo-16k'
                elif model_name == 'gpt-3.5-turbo':
                    model_name = 'gpt-3.5-turbo-16k'
                else:
                    raise e
                print("max context length reached, retrying with " + model_name)
                chatcompletion_kwargs = get_apiconfig_by_model(model_name)
                chatcompletion_kwargs.update(kwargs)
                chatcompletion_kwargs.pop('schema_error_retry', None)

                response = openai.ChatCompletion.create(
                    **chatcompletion_kwargs)
                response = json.loads(str(response))
            else:
                raise e

        return response

else:
    from openai import AuthenticationError, PermissionDeniedError, BadRequestError
    RETRY_ERRORS = (AuthenticationError, PermissionDeniedError,
                    BadRequestError, AssertionError)
    @retry(
        retry=retry_if_not_exception_type(RETRY_ERRORS),
        stop=stop_after_attempt(CONFIG.max_retry_times+3), 
        wait=wait_chain(*[wait_none() for _ in range(3)]+[wait_exponential(min=61, max=293)]),
        reraise=True,)
    def chatcompletion_request(**kwargs):
        model_name = get_model_name(
            kwargs.pop("model", CONFIG.default_completion_kwargs["model"])
        )
        logger.debug("chatcompletion: using " + model_name)
        chatcompletion_kwargs = get_apiconfig_by_model(model_name)

        
        request_timeout = kwargs.pop("request_timeout", 60)
        if "base_url" in chatcompletion_kwargs:
            base_url = chatcompletion_kwargs.pop("base_url", None)
        else:
            base_url = chatcompletion_kwargs.pop("api_base", None)
        api_key = chatcompletion_kwargs.pop("api_key", None)
        chatcompletion_kwargs.update(kwargs)
        client =  openai.OpenAI(api_key=api_key, base_url=base_url,timeout=request_timeout)

        completions = client.chat.completions.create(**chatcompletion_kwargs)
        response = completions.model_dump()
        if response["choices"][0]["finish_reason"] == "length":
            raise BadRequestError("maximum context length exceeded", None)
            
        return response