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


@openai_responses.mock()
def test_create_thread_run(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo",
    )

    run = client.beta.threads.create_and_run(assistant_id=assistant.id)

    assert run.id
    assert run.assistant_id == assistant.id
    assert run.instructions == assistant.instructions
    assert run.tools == assistant.tools

    assert openai_mock.beta.assistants.create.calls.call_count == 1
    assert openai_mock.beta.threads.create_and_run.calls.call_count == 1


@openai_responses.mock()
def test_list_runs(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo",
    )

    thread = client.beta.threads.create()

    for _ in range(10):
        client.beta.threads.runs.create(
            thread.id,
            assistant_id=assistant.id,
        )

    runs = client.beta.threads.runs.list(thread.id)

    assert len(runs.data) == 10

    assert openai_mock.beta.assistants.create.calls.call_count == 1
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.runs.create.calls.call_count == 10
    assert openai_mock.beta.threads.runs.list.calls.call_count == 1


@openai_responses.mock()
def test_retrieve_run(openai_mock: OpenAIMock):
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

    found = client.beta.threads.runs.retrieve(run.id, thread_id=thread.id)

    assert found.id == run.id

    assert openai_mock.beta.assistants.create.calls.call_count == 1
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.runs.create.calls.call_count == 1
    assert openai_mock.beta.threads.runs.retrieve.calls.call_count == 1


@openai_responses.mock()
def test_update_run(openai_mock: OpenAIMock):
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
        metadata={"foo": "1"},
    )

    updated = client.beta.threads.runs.update(
        run.id,
        thread_id=thread.id,
        metadata={"foo": "2"},
    )

    assert updated.id == run.id
    assert run.metadata == {"foo": "1"}
    assert updated.metadata == {"foo": "2"}

    assert openai_mock.beta.assistants.create.calls.call_count == 1
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.runs.create.calls.call_count == 1
    assert openai_mock.beta.threads.runs.update.calls.call_count == 1
