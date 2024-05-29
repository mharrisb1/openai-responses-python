import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_create_vector_store(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    vector_store = client.beta.vector_stores.create(name="Support FAQ")

    assert vector_store.name == "Support FAQ"
    assert openai_mock.beta.vector_stores.create.route.call_count == 1
