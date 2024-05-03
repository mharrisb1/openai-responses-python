import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_create_thread(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    thread = client.beta.threads.create()

    assert thread.id
    assert openai_mock.beta.threads.create.calls.call_count == 1


@openai_responses.mock()
def test_retrieve_thread(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    thread = client.beta.threads.create()
    found = client.beta.threads.retrieve(thread.id)

    assert found.id == thread.id
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.retrieve.calls.call_count == 1


@openai_responses.mock()
def test_update_thread(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    thread = client.beta.threads.create(metadata={"foo": "bar"})
    updated = client.beta.threads.update(thread.id, metadata={"foo": "baz"})

    assert updated.id == thread.id
    assert thread.metadata == {"foo": "bar"}
    assert updated.metadata == {"foo": "baz"}
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.update.calls.call_count == 1
