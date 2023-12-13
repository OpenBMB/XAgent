from unittest import mock
from XAgent.ai_functions.request.openai import chatcompletion_request
import importlib.metadata as metadata

openai_version = metadata.version("openai")


def test_model_alias():
    if openai_version >= "1.0.0":
        # Mock the OpenAI client and response
        with mock.patch("openai.OpenAI") as mock_openai:
            mock_client = mock_openai.return_value
            mock_response = mock_client.chat.completions.create.return_value

            # Mock the model_dump() method
            mock_model_dump = mock_response.model_dump
            mock_model_dump.return_value = {
                "choices": [
                    {
                        "finish_reason": "stop",
                        "index": 0,
                        "message": {"content": "Hello, World!"},
                    }
                ]
            }

            # Call the function
            response = chatcompletion_request(
                model="gpt-4-turbo", prompt="Hello, world"
            )

            # Assert that the response is as expected
            assert response["choices"][0]["finish_reason"] == "stop"
            assert response["choices"][0]["index"] == 0
            assert response["choices"][0]["message"]["content"] == "Hello, World!"

    else:
        with mock.patch("openai.ChatCompletion") as mock_create:
            mock_response_data = """{"choices": [{"finish_reason": "stop", "index": 0, "message": {"content": "Hello, World!"}}]}"""

            mock_create.create.return_value = mock_response_data

            response = chatcompletion_request(
                model="gpt-4-turbo", prompt="Hello, world"
            )
            assert response["choices"][0]["message"]["content"] == "Hello, World!"

    print(f"Your OpenAI version is {openai_version}, Successful test")


# Run the test
if __name__ == "__main__":
    test_model_alias()