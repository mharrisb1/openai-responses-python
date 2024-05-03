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


@openai_responses.mock()
def test_list_assistants(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    for _ in range(10):
        client.beta.assistants.create(
            instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
            name="Math Tutor",
            tools=[{"type": "code_interpreter"}],
            model="gpt-4-turbo",
        )

    assistants = client.beta.assistants.list()

    assert len(assistants.data) == 10
    assert openai_mock.beta.assistants.create.calls.call_count == 10
    assert openai_mock.beta.assistants.list.calls.call_count == 1


@openai_responses.mock()
def test_retrieve_assistant(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo",
    )

    found = client.beta.assistants.retrieve(assistant.id)

    assert assistant.name == "Math Tutor"
    assert found.name == assistant.name
    assert openai_mock.beta.assistants.create.calls.call_count == 1
    assert openai_mock.beta.assistants.retrieve.calls.call_count == 1


@openai_responses.mock()
def test_update_assistant(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo",
    )

    updated = client.beta.assistants.update(
        assistant.id,
        name="Math Tutor (Slim)",
        model="gpt-3.5-turbo",
    )

    assert updated.id == assistant.id
    assert assistant.name == "Math Tutor"
    assert assistant.model == "gpt-4-turbo"
    assert updated.name == "Math Tutor (Slim)"
    assert updated.model == "gpt-3.5-turbo"
    assert openai_mock.beta.assistants.create.calls.call_count == 1
    assert openai_mock.beta.assistants.update.calls.call_count == 1


@openai_responses.mock()
def test_delete_assistant(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo",
    )

    assert client.beta.assistants.delete(assistant.id).deleted
    assert openai_mock.beta.assistants.create.calls.call_count == 1
    assert openai_mock.beta.assistants.delete.calls.call_count == 1
