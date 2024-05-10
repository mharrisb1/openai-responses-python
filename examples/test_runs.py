import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_create_run(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo",
    )

    thread = client.beta.threads.create()

    run = client.beta.threads.runs.create(
        thread.id,
        assistant_id=assistant.id,
    )

    assert run.id
    assert run.thread_id == thread.id
    assert run.assistant_id == assistant.id
    assert run.instructions == assistant.instructions
    assert run.tools == assistant.tools

    assert openai_mock.beta.assistants.create.calls.call_count == 1
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.runs.create.calls.call_count == 1
