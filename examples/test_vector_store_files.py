import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_create_vector_file_store(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    vector_store = client.beta.vector_stores.create(name="Support FAQ")
    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )

    vector_store_file = client.beta.vector_stores.files.create(
        vector_store_id=vector_store.id,
        file_id=file.id,
    )

    assert vector_store_file.vector_store_id == vector_store.id
    assert vector_store_file.id == file.id

    assert openai_mock.files.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.create.route.call_count == 1
    assert openai_mock.beta.vector_stores.files.create.route.call_count == 1
