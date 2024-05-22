# Streaming

!!! info

    ✨ New in v0.4.0

OpenAI uses [server-sent events](https://en.wikipedia.org/wiki/Server-sent_events) (SSE) for streaming. Those types of responses are slightly different than standard HTTP responses.

The content in the response is an iterable stream of data. Decoded, it would look like this:

```text
event: thread.run.created
data: {"id":"run_123","object":"thread.run","created_at":1710330640,"assistant_id":"asst_123","thread_id":"thread_123","status":"queued","started_at":null,"expires_at":1710331240,"cancelled_at":null,"failed_at":null,"completed_at":null,"required_action":null,"last_error":null,"model":"gpt-4-turbo","instructions":null,"tools":[],"metadata":{},"temperature":1.0,"top_p":1.0,"max_completion_tokens":null,"max_prompt_tokens":null,"truncation_strategy":{"type":"auto","last_messages":null},"incomplete_details":null,"usage":null,"response_format":"auto","tool_choice":"auto"}}

...

event: thread.run.completed
data: {"id":"run_123","object":"thread.run","created_at":1710330640,"assistant_id":"asst_123","thread_id":"thread_123","status":"completed","started_at":1710330641,"expires_at":null,"cancelled_at":null,"failed_at":null,"completed_at":1710330642,"required_action":null,"last_error":null,"model":"gpt-4-turbo","instructions":null,"tools":[],"metadata":{},"temperature":1.0,"top_p":1.0,"max_completion_tokens":null,"max_prompt_tokens":null,"truncation_strategy":{"type":"auto","last_messages":null},"incomplete_details":null,"usage":{"prompt_tokens":20,"completion_tokens":11,"total_tokens":31},"response_format":"auto","tool_choice":"auto"}}

event: done
data: [DONE]
```

To mock that, an `EventStream` and `AsyncEventStream` classes are provided.

These classes are meant to be inherited and built on top of. The main part that you would need to worry about is overriding the `generate` method. This method yields `Event` objects which can be encoded as SSE events and the resulting stream will look like the example above.

The stream object can be passed in to an HTTPX response as an argument for `content`. To do this, you'll need to also make use of [function responses](responses.md#function).

## Example

Here's an example using chat completions API.

```python linenums="1" hl_lines="13 15 33 70 71"
from typing import Generator
from typing_extensions import override

import openai
from openai.types.chat import ChatCompletionChunk

import openai_responses
from openai_responses import OpenAIMock
from openai_responses.streaming import Event, EventStream
from openai_responses.ext.httpx import Request, Response


class CreateChatCompletionEventStream(EventStream):  # (1)
    @override
    def generate(self) -> Generator[Event, None, None]:  # (2)
        chunk = ChatCompletionChunk.model_validate(
            {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": 1694268190,
                "model": "gpt-4o",
                "system_fingerprint": "fp_44709d6fcb",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": ""},
                        "logprobs": None,
                        "finish_reason": None,
                    }
                ],
            }
        )
        yield self.event(None, chunk)  # (3)

        chunk = ChatCompletionChunk.model_validate(
            {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": 1694268190,
                "model": "gpt-4o",
                "system_fingerprint": "fp_44709d6fcb",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "Hello"},
                        "logprobs": None,
                        "finish_reason": None,
                    }
                ],
            }
        )
        yield self.event(None, chunk)

        chunk = ChatCompletionChunk.model_validate(
            {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": 1694268190,
                "model": "gpt-4o",
                "system_fingerprint": "fp_44709d6fcb",
                "choices": [
                    {"index": 0, "delta": {}, "logprobs": None, "finish_reason": "stop"}
                ],
            }
        )
        yield self.event(None, chunk)


def create_chat_completion_response(request: Request) -> Response:
    stream = CreateChatCompletionEventStream()  # (4)
    return Response(201, content=stream)  # (5)


@openai_responses.mock()
def test_create_chat_completion_stream(openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = create_chat_completion_response

    client = openai.Client(api_key="sk-fake123")
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        stream=True,
    )

    received_chunks = 0

    for chunk in completion:
        received_chunks += 1
        assert chunk.id

    assert received_chunks == 3
```

1. Your stream class must inherit from either `EventStream` or `AsyncEventStream`
2. Override the `generate` method
3. Yield an event. You can include an `event.event` name.
4. Construct the stream object
5. Pass the stream as `content` on the response object

More examples can be found in the [examples](https://github.com/mharrisb1/openai-responses-python/tree/main/examples) directory in the repo:

- [examples/test_streaming.py](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_streaming.py)
- [examples/test_streaming_async.py](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_streaming_async.py)
- [examples/test_streaming_simple.py](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_streaming_simple.py)
