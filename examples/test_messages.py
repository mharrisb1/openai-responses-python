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
    assert message.thread_id == thread.id
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.messages.create.calls.call_count == 1


@openai_responses.mock()
def test_list_messages(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")
    thread = client.beta.threads.create()

    for i in range(10):
        client.beta.threads.messages.create(
            thread.id,
            content=f"Hello, {i}!",
            role="user",
        )

    messages = client.beta.threads.messages.list(thread.id)

    assert len(messages.data) == 10
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.messages.create.calls.call_count == 10
    assert openai_mock.beta.threads.messages.list.calls.call_count == 1


@openai_responses.mock()
def test_retrieve_message(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread.id,
        content="Hello!",
        role="user",
    )
    found = client.beta.threads.messages.retrieve(message.id, thread_id=thread.id)

    assert found.id == message.id
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.messages.create.calls.call_count == 1
    assert openai_mock.beta.threads.messages.retrieve.calls.call_count == 1


@openai_responses.mock()
def test_update_message(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread.id,
        content="Hello!",
        role="user",
        metadata={"foo": "1"},
    )
    updated = client.beta.threads.messages.update(
        message.id,
        thread_id=thread.id,
        metadata={"foo": "2"},
    )

    assert updated.id == message.id
    assert message.metadata == {"foo": "1"}
    assert updated.metadata == {"foo": "2"}
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.messages.create.calls.call_count == 1
    assert openai_mock.beta.threads.messages.update.calls.call_count == 1


@openai_responses.mock()
def test_delete_message(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread.id,
        content="Hello!",
        role="user",
        metadata={"foo": "1"},
    )

    assert client.beta.threads.messages.delete(message.id, thread_id=thread.id).deleted
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.messages.create.calls.call_count == 1
    assert openai_mock.beta.threads.messages.delete.calls.call_count == 1
