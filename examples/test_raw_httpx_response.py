import pytest

import openai
from openai import APIStatusError

import openai_responses
from openai_responses import OpenAIMock, Response


@openai_responses.mock()
def test_create_chat_completion(openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = Response(500)

    client = openai.Client(api_key="sk-fake123", max_retries=0)

    with pytest.raises(APIStatusError):
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        )
