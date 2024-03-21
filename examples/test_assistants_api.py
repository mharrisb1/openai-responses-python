import pytest
from openai import OpenAI, AsyncOpenAI, NotFoundError

import openai_responses
from openai_responses import AssistantsMock


@openai_responses.mock.beta.assistants()
def test_create_assistant(assistants_mock: AssistantsMock):
    client = OpenAI(api_key="fakeKey")
    my_assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4",
    )
    assert my_assistant.name == "Math Tutor"
    assert my_assistant.model == "gpt-4"
    assert assistants_mock.create.route.calls.call_count == 1


@pytest.mark.asyncio
@openai_responses.mock.beta.assistants()
async def test_async_create_assistant(assistants_mock: AssistantsMock):
    client = AsyncOpenAI(api_key="fakeKey")
    my_assistant = await client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4",
    )
    assert my_assistant.name == "Math Tutor"
    assert my_assistant.model == "gpt-4"
    assert assistants_mock.create.route.calls.call_count == 1


@openai_responses.mock.beta.assistants()
def test_list_assistants(assistants_mock: AssistantsMock):
    client = OpenAI(api_key="fakeKey")
    for _ in range(21):
        client.beta.assistants.create(model="gpt-4")

    assistants = client.beta.assistants.list()
    assert len(assistants.data) == 20
    assert assistants_mock.list.route.calls.call_count == 1


@openai_responses.mock.beta.assistants()
def test_retrieve_assistant(assistants_mock: AssistantsMock):
    client = OpenAI(api_key="fakeKey")

    with pytest.raises(NotFoundError):
        client.beta.assistants.retrieve("invalid-id")

    asst = client.beta.assistants.create(model="gpt-4")
    found = client.beta.assistants.retrieve(asst.id)
    assert found.id == asst.id
    assert assistants_mock.retrieve.route.calls.call_count == 2


@openai_responses.mock.beta.assistants()
def test_update_assistant(assistants_mock: AssistantsMock):
    client = OpenAI(api_key="fakeKey")

    with pytest.raises(NotFoundError):
        client.beta.assistants.update("invalid-id", model="gpt-4")

    asst = client.beta.assistants.create(model="gpt-4")
    updated = client.beta.assistants.update(asst.id, model="gpt-3.5-turbo")

    assert updated.id == asst.id
    assert updated.model == "gpt-3.5-turbo"
    assert assistants_mock.update.route.calls.call_count == 2


@openai_responses.mock.beta.assistants()
def test_delete_assistant(assistants_mock: AssistantsMock):
    client = OpenAI(api_key="fakeKey")

    assert not client.beta.assistants.delete("invalid-id").deleted

    asst = client.beta.assistants.create(model="gpt-4")
    assert client.beta.assistants.delete(asst.id).deleted
    assert assistants_mock.delete.route.calls.call_count == 2
