# Quickstart

Other examples are available in the [examples](https://github.com/mharrisb1/openai-responses-python/tree/main/examples) directory.

## Chat Completions

This is an example of testing a call to `POST https://api.openai.com/v1/chat/completions`

=== "Sync"

    ```python title="test_chat_completion_api.py"
    from openai import OpenAI

    import openai_responses

    @openai_responses.mock.chat.completions(
        choices=[
            {"message": {"content": "Hello, how can I help?"}},
            {"message": {"content": "Hi! I'm here to help!"}},
            {"message": {"content": "How can I help?"}},
        ],
    )
    def test_create_completion_with_multiple_choices():
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
    ```

=== "Async"

    ```python title="test_chat_completion_api.py"
    import pytest

    from openai import AsyncOpenAI

    import openai_responses

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
    ```
