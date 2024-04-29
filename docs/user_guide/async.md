# Async

Async is supported out of the box and you shouldn't have to do anything different from defining synchronous tests. The only additional bit of setup needed is you need to also install the [pytest-asyncio](https://pypi.org/project/pytest-asyncio/) plugin and mark the test as async.

View the below examples to see the difference between using async and not.

=== "Sync"

    ```python linenums="1"
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

    ```python linenums="1"
    import pytest

    from openai import AsyncOpenAI

    import openai_responses


    @pytest.mark.asyncio
    @openai_responses.mock.chat.completions(
        choices=[
            {"message": {"content": "Hello, how can I help?"}},
            {"message": {"content": "Hi! I'm here to help!"}},
            {"message": {"content": "How can I help?"}},
        ],
    )
    async def test_create_completion_with_multiple_choices():
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
    ```
