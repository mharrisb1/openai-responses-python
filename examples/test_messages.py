import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_create_message(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread.id,
        content="Hello!",
        role="user",
    )

    assert message.id
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.messages.create.calls.call_count == 1
