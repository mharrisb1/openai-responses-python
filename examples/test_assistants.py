import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_create_assistant(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo",
    )

    assert assistant.name == "Math Tutor"
    assert openai_mock.beta.assistants.create.calls.call_count == 1
