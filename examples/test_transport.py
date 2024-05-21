import openai
from openai import DefaultHttpxClient

from openai_responses import OpenAIMock
from openai_responses.ext.httpx import MockTransport


def test_create_chat_completion():
    openai_mock = OpenAIMock()
    openai_mock.chat.completions.create.response = {
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {
                    "content": "Hello! How can I help?",
                    "role": "assistant",
                },
            }
        ]
    }

    client = openai.Client(
        api_key="sk-fake123",
        http_client=DefaultHttpxClient(
            transport=MockTransport(openai_mock.router.handler)
        ),
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
    assert openai_mock.chat.completions.create.calls.call_count == 1
