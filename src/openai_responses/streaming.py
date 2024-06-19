import json
from typing import AsyncIterator, Generator, Generic, Optional, TypeVar, Union

from openai.types.beta import AssistantStreamEvent
from openai.types.chat import ChatCompletionChunk

from ._utils.aio import make_async_generator
from ._utils.serde import model_dict

__all__ = ["EventStream", "AsyncEventStream"]

M = TypeVar("M", bound=Union[AssistantStreamEvent, ChatCompletionChunk])


class BaseEventStream(Generic[M]):
    @staticmethod
    def _dump_event(event: M) -> tuple[Optional[bytes], Optional[bytes]]:
        if hasattr(event, "event") and hasattr(event, "data"):
            event_type: Optional[str] = getattr(event, "event", None)
            data: Optional[AssistantStreamEvent] = getattr(event, "data", None)
            if event_type is not None and data is not None:
                encoded_event = f"event: {event_type}\n".encode()
                encoded_data = f"data: {json.dumps(model_dict(data))}\n\n".encode()
                return encoded_event, encoded_data
        encoded_data = f"data: {json.dumps(model_dict(event))}\n\n".encode()
        return None, encoded_data

    def generate(self) -> Generator[M, None, None]:
        raise NotImplementedError


class EventStream(BaseEventStream[M]):
    """Event stream helper for building mock OpenAI server sent event stream"""

    def __iter__(self) -> Generator[bytes, None, None]:
        for _event in self.generate():
            t, d = self._dump_event(_event)
            if t:
                yield t
            if d:
                yield d

        yield b"event: done\n"
        yield b"data: [DONE]\n\n"


class AsyncEventStream(BaseEventStream[M]):
    """Async event stream helper for building mock OpenAI server sent event stream"""

    async def __aiter__(self) -> AsyncIterator[bytes]:
        async for _event in make_async_generator(self.generate()):
            t, d = self._dump_event(_event)
            if t:
                yield t
            if d:
                yield d
        yield b"event: done\n"
        yield b"data: [DONE]\n\n"
