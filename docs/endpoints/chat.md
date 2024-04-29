# Chat

!!! tip

    See [examples](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_chat_completion_api.py) for more

## Decorator Arguments

- `latency` - synthetic latency in seconds to introduce to the call(s). Defaults to `0.0`.
- `failures` - number of failures to simulate. Defaults to `0`.
- `choices` - list of model choice responses. Defaults to `[]`.

## Create chat completion

=== "Sync"

    ```python linenums="1"
    from openai import OpenAI

    import openai_responses


    @openai_responses.mock.chat.completions(
        choices=[
            {"message": {"content": "Hello, how can I help?"}},
        ]
    )
    def test_create_completion():
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
        ]
    )
    async def test_create_completion():
        client = AsyncOpenAI(api_key="fakeKey")
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        )
        assert len(completion.choices) == 1
        assert completion.choices[0].message.content == "Hello, how can I help?"
    ```

=== "With Mocker Class"

    ```python linenums="1" hl_lines="4 12 23"
    from openai import OpenAI

    import openai_responses
    from openai_responses import ChatCompletionMock # (1)


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
    ```

    1.  See [mockers guide](../user_guide/mocks.md) for more
