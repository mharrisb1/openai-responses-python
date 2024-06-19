from typing import Generator
from typing_extensions import override

import openai
from openai.types.chat import ChatCompletionChunk

import openai_responses
from openai_responses import OpenAIMock
from openai_responses.streaming import EventStream
from openai_responses.ext.httpx import Request, Response


class CreateChatCompletionEventStream(EventStream[ChatCompletionChunk]):
    @override
    def generate(self) -> Generator[ChatCompletionChunk, None, None]:
        yield ChatCompletionChunk.model_validate(
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

        yield ChatCompletionChunk.model_validate(
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

        yield ChatCompletionChunk.model_validate(
            {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": 1694268190,
                "model": "gpt-4o",
                "system_fingerprint": "fp_44709d6fcb",
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "logprobs": None,
                        "finish_reason": "stop",
                    }
                ],
            }
        )


def create_chat_completion_response(request: Request) -> Response:
    stream = CreateChatCompletionEventStream()
    return Response(201, content=stream, request=request)


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
