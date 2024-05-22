from openai import AzureOpenAI

import openai_responses
from openai_responses import OpenAIMock

AZURE_ENDPOINT = "https://example-endpoint.openai.azure.com"


@openai_responses.mock(base_url=AZURE_ENDPOINT)
def test_create_chat_completion(openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = {
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"content": "Hello! How can I help?", "role": "assistant"},
            }
        ]
    }

    client = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key="fakeKey123",
        api_version="2024-02-01",
    )

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
    )

    assert len(completion.choices) == 1
    assert completion.choices[0].message.content == "Hello! How can I help?"
    assert openai_mock.chat.completions.create.route.call_count == 1
