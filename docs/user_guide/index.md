# User Guide

To mock API calls within a test function you must decorate the test function with a mock decorator. Each endpoint has its own decorator.
You can [chain](chaining.md) decorators if your test calls more than one endpoint. Each decorator has the following arguments:

- `latency` - synthetic latency in seconds to introduce to the call(s). Defaults to `0.0`.
- `failures` - number of failures to simulate. Defaults to `0`.

Some decorators will have additional arguments.

View available [endpoints](../endpoints/index.md).

## Example

=== "Sync"

    ```python linenums="1" hl_lines="6 7 12"
    from openai import OpenAI

    import openai_responses


    @openai_responses.mock.chat.completions( # (1)
        choices=[ # (2)
            {"message": {"content": "Hello, how can I help?"}},
            {"message": {"content": "Hi! I'm here to help!"}},
            {"message": {"content": "How can I help?"}},
        ],
        latency=5, # (3)
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

    1. Mocker decorators will follow the same interface as the API client
    2. This mocker has an additional argument for `choices`
    3. Common argument for `latency`

=== "Async"

    ```python linenums="1" hl_lines="9 10 15"
    import pytest

    from openai import AsyncOpenAI

    import openai_responses


    @pytest.mark.asyncio
    @openai_responses.mock.chat.completions( # (1)
        choices=[ # (2)
            {"message": {"content": "Hello, how can I help?"}},
            {"message": {"content": "Hi! I'm here to help!"}},
            {"message": {"content": "How can I help?"}},
        ],
        latency=5, # (3)
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

    1. Mocker decorators will follow the same interface as the API client
    2. This mocker has an additional argument for `choices`
    3. Common argument for `latency`