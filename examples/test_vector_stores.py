import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_create_vector_store(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    vector_store = client.beta.vector_stores.create(name="Support FAQ")

    assert vector_store.name == "Support FAQ"
    assert openai_mock.beta.vector_stores.create.route.call_count == 1


@openai_responses.mock()
def test_list_vector_stores(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    for i in range(10):
        client.beta.vector_stores.create(name=f"vector-store-{i}")

    vector_stores = client.beta.vector_stores.list()

    assert len(vector_stores.data) == 10
    assert openai_mock.beta.vector_stores.create.route.call_count == 10
    assert openai_mock.beta.vector_stores.list.route.call_count == 1


@openai_responses.mock()
def test_retrieve_vector_store(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    vector_store = client.beta.vector_stores.create(name="Support FAQ")

    found = client.beta.vector_stores.retrieve(vector_store.id)

    assert vector_store.name == "Support FAQ"
    assert found.name == vector_store.name
    assert openai_mock.beta.vector_stores.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.retrieve.route.call_count == 1


@openai_responses.mock()
def test_update_vector_store(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    vector_store = client.beta.vector_stores.create(name="Support FAQ")

    updated = client.beta.vector_stores.update(
        vector_store.id,
        name="Support FAQ Updated",
    )

    assert updated.id == vector_store.id
    assert updated.name == "Support FAQ Updated"
    assert openai_mock.beta.vector_stores.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.update.route.call_count == 1


@openai_responses.mock()
def test_delete_vector_store(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    vector_store = client.beta.vector_stores.create(name="Support FAQ")

    assert client.beta.vector_stores.delete(vector_store.id).deleted
    assert openai_mock.beta.vector_stores.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.delete.route.call_count == 1
