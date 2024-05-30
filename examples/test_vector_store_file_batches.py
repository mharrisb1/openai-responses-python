import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_create_vector_store_file_batch(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    vector_store = client.beta.vector_stores.create(name="Support FAQ")
    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )

    vector_store_file_batch = client.beta.vector_stores.file_batches.create(
        vector_store_id=vector_store.id,
        file_ids=[file.id],
    )

    assert vector_store_file_batch.vector_store_id == vector_store.id
    assert vector_store_file_batch.file_counts.completed == 1

    assert openai_mock.files.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.file_batches.create.route.call_count == 1


@openai_responses.mock()
def test_retrieve_vector_store_file_batch(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    vector_store = client.beta.vector_stores.create(name="Support FAQ")
    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )

    vector_store_file_batch = client.beta.vector_stores.file_batches.create(
        vector_store_id=vector_store.id,
        file_ids=[file.id],
    )

    found = client.beta.vector_stores.file_batches.retrieve(
        vector_store_file_batch.id, vector_store_id=vector_store.id
    )

    assert found.id == vector_store_file_batch.id

    assert openai_mock.files.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.file_batches.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.file_batches.retrieve.route.call_count == 1


@openai_responses.mock()
def test_cancel_vector_store_file_batch(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    vector_store = client.beta.vector_stores.create(name="Support FAQ")
    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )

    vector_store_file_batch = client.beta.vector_stores.file_batches.create(
        vector_store_id=vector_store.id,
        file_ids=[file.id],
    )

    cancelled = client.beta.vector_stores.file_batches.cancel(
        vector_store_file_batch.id, vector_store_id=vector_store.id
    )

    assert cancelled.id == vector_store_file_batch.id
    assert cancelled.status == "cancelled"

    assert openai_mock.files.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.file_batches.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.file_batches.cancel.route.call_count == 1


@openai_responses.mock()
def test_list_files_for_vector_store_file_batch(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    vector_store = client.beta.vector_stores.create(name="Support FAQ")
    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )

    vector_store_file_batch = client.beta.vector_stores.file_batches.create(
        vector_store_id=vector_store.id,
        file_ids=[file.id],
    )

    files = client.beta.vector_stores.file_batches.list_files(
        vector_store_file_batch.id,
        vector_store_id=vector_store.id,
    )

    assert len(files.data) == 1

    assert openai_mock.files.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.file_batches.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.file_batches.list_files.route.call_count == 1
