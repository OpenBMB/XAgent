from unittest import mock
from XAgent.ai_functions.request.openai import chatcompletion_request, chat_completion_to_dict
import importlib.metadata as metadata
openai_version = metadata.version("openai")

# Set OpenAI version to 1.x
if openai_version >= "1.0.0":
    # Mock the OpenAI client and response
    with mock.patch("openai.OpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_response = mock_client.chat.completions.create.return_value
        mock_response.choices[0].finish_reason = "stop"
        mock_response.choices[0].index = 0
        mock_response.choices[0].message.content = "Hello, World!"

        # Call the function
        response = chatcompletion_request(model="gpt-3.5-turbo-16k", prompt="Hello")
        # Assert that the response is as expected
        assert response["choices"][0]["finish_reason"] == "stop"
        assert response["choices"][0]["index"] == 0
        assert response["choices"][0]["message"]["content"] == "Hello, World!"
        print(f"Your openapi version is {openai_version}, Successful test")
else:
    print(f"We support your current version of openapi, Your openapi version is {openai_version}")