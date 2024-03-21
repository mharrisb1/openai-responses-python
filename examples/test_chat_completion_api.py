import pytest
from openai import OpenAI, AsyncOpenAI

import openai_responses
from openai_responses import ChatCompletionMock


@openai_responses.mock.chat.completions(
    choices=[
        {"message": {"content": "Hello, how can I help?"}},
    ]
)
def test_create_completion(chat_completion_mock: ChatCompletionMock):
    client = OpenAI(api_key="fakeKey")
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
    )
    assert len(completion.choices) == 1
    assert completion.choices[0].message.content == "Hello, how can I help?"
    assert chat_completion_mock.create.route.calls.call_count == 1


@openai_responses.mock.chat.completions(
    choices=[
        {"message": {"content": "Hello, how can I help?"}},
        {"message": {"content": "Hi! I'm here to help!"}},
        {"message": {"content": "How can I help?"}},
    ]
)
def test_create_completion_with_multiple_choices(
    chat_completion_mock: ChatCompletionMock,
):
    client = OpenAI(api_key="fakeKey")
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        n=3,
    )
    assert len(completion.choices) == 3
    assert chat_completion_mock.create.route.calls.call_count == 1


@pytest.mark.asyncio
@openai_responses.mock.chat.completions(
    choices=[
        {"message": {"content": "Hello, how can I help?"}},
        {"message": {"content": "Hi! I'm here to help!"}},
        {"message": {"content": "How can I help?"}},
    ]
)
async def test_async_create_completion_with_multiple_choices(
    chat_completion_mock: ChatCompletionMock,
):
    client = AsyncOpenAI(api_key="fakeKey")
    completion = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        n=3,
    )
    assert len(completion.choices) == 3
    assert chat_completion_mock.create.route.calls.call_count == 1
