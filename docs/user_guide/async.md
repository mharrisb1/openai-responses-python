# Async

Async is supported out of the box and you don't have to do anything different from defining synchronous tests. The only additional bit of setup needed is you need to also install the [pytest-asyncio](https://pypi.org/project/pytest-asyncio/) plugin and mark the test as async.

=== "Async"

    ```python linenums="1"
    import pytest

    import openai

    import openai_responses
    from openai_responses import OpenAIMock


    @pytest.mark.asyncio
    @openai_responses.mock()
    async def test_async_create_chat_completion(openai_mock: OpenAIMock):
        openai_mock.chat.completions.create.response = {
            "choices": [
                {
                    "index": 0,
                    "finish_reason": "stop",
                    "message": {"content": "Hello! How can I help?", "role": "assistant"},
                }
            ]
        }

        client = openai.AsyncClient(api_key="sk-fake123")
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        )

        assert len(completion.choices) == 1
        assert completion.choices[0].message.content == "Hello! How can I help?"
        assert openai_mock.chat.completions.create.calls.call_count == 1
    ```

=== "Sync"

    ```python linenums="1"
    import openai

    import openai_responses
    from openai_responses import OpenAIMock


    @openai_responses.mock()
    def test_create_chat_completion(openai_mock: OpenAIMock):
        openai_mock.chat.completions.create.response = {
            "choices": [
                {
                    "index": 0,
                    "finish_reason": "stop",
                    "message": {"content": "Hello! How can I help?", "role": "assistant"},
                }
            ]
        }

        client = openai.Client(api_key="sk-fake123")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        )

        assert len(completion.choices) == 1
        assert completion.choices[0].message.content == "Hello! How can I help?"
        assert openai_mock.chat.completions.create.calls.call_count == 1
    ```
