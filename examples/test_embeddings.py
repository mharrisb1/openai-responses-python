import openai

import openai_responses
from openai_responses import OpenAIMock


EMBEDDING = [0.0023064255, -0.009327292, -0.0028842222]


@openai_responses.mock()
def test_create_embedding(openai_mock: OpenAIMock):
    openai_mock.embeddings.create.response = {
        "data": [
            {
                "object": "embedding",
                "embedding": EMBEDDING,
                "index": 0,
            },
        ]
    }

    client = openai.Client(api_key="sk-fake123")
    embeddings = client.embeddings.create(
        model="text-embedding-ada-002",
        input="The food was delicious and the waiter...",
        encoding_format="float",
    )

    assert embeddings.model == "text-embedding-ada-002"
    assert len(embeddings.data) == 1
    assert embeddings.data[0].embedding == EMBEDDING
    assert embeddings.data[0]
    assert openai_mock.embeddings.create.route.call_count == 1
