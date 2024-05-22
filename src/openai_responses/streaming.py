import json
from dataclasses import dataclass
from typing import AsyncIterator, Generator, Literal, Optional, Tuple, Union, overload

from openai.types import ErrorObject
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from openai.types.beta.thread import Thread
from openai.types.beta.threads.message import Message
from openai.types.beta.threads.message_delta import MessageDelta
from openai.types.beta.threads.run import Run
from openai.types.beta.threads.runs.run_step import RunStep
from openai.types.beta.threads.runs.run_step_delta import RunStepDelta

from ._utils.aio import make_async_generator
from ._utils.serde import model_dict

__all__ = ["Event", "EventStream", "AsyncEventStream"]

EventType = Literal[
    "thread.created",
    "thread.run.created",
    "thread.run.queued",
    "thread.run.in_progress",
    "thread.run.requires_action",
    "thread.run.completed",
    "thread.run.incomplete",
    "thread.run.failed",
    "thread.run.cancelling",
    "thread.run.cancelled",
    "thread.run.expired",
    "thread.run.step.created",
    "thread.run.step.in_progress",
    "thread.run.step.delta",
    "thread.run.step.completed",
    "thread.run.step.failed",
    "thread.run.step.cancelled",
    "thread.run.step.expired",
    "thread.message.created",
    "thread.message.in_progress",
    "thread.message.delta",
    "thread.message.completed",
    "thread.message.incomplete",
    "error",
]
EventData = Union[
    ChatCompletionChunk,
    Thread,
    Run,
    RunStep,
    RunStepDelta,
    Message,
    MessageDelta,
    ErrorObject,
]


@dataclass(frozen=True)
class Event:
    event: Optional[EventType]
    data: EventData

    def to_sse_event(self) -> Tuple[Optional[bytes], Optional[bytes]]:
        encoded_event = f"event: {self.event}\n".encode() if self.event else None
        encoded_data = f"data: {json.dumps(model_dict(self.data))}\n\n".encode()
        return encoded_event, encoded_data


class BaseEventStream:
    @staticmethod
    @overload
    def event(event: Literal["thread.created"], data: Thread) -> Event: ...

    @staticmethod
    @overload
    def event(
        event: Literal[
            "thread.run.created",
            "thread.run.queued",
            "thread.run.in_progress",
            "thread.run.requires_action",
            "thread.run.completed",
            "thread.run.incomplete",
            "thread.run.failed",
            "thread.run.cancelling",
            "thread.run.cancelled",
            "thread.run.expired",
        ],
        data: Run,
    ) -> Event: ...

    @staticmethod
    @overload
    def event(
        event: Literal[
            "thread.run.step.created",
            "thread.run.step.in_progress",
            "thread.run.step.completed",
            "thread.run.step.failed",
            "thread.run.step.cancelled",
            "thread.run.step.expired",
        ],
        data: RunStep,
    ) -> Event: ...

    @staticmethod
    @overload
    def event(event: Literal["thread.run.step.delta"], data: RunStepDelta) -> Event: ...

    @staticmethod
    @overload
    def event(
        event: Literal[
            "thread.message.created",
            "thread.message.in_progress",
            "thread.message.completed",
            "thread.message.incomplete",
        ],
        data: Message,
    ) -> Event: ...

    @staticmethod
    @overload
    def event(event: Literal["thread.message.delta"], data: MessageDelta) -> Event: ...

    @staticmethod
    @overload
    def event(event: Literal["error"], data: ErrorObject) -> Event: ...

    @staticmethod
    @overload
    def event(event: None, data: ChatCompletionChunk) -> Event: ...

    @staticmethod
    def event(event: Optional[EventType], data: EventData) -> Event:
        """
        Create a server sent event payload with event.type (optional) and event.data payloads
        """
        return Event(event, data)

    def generate(self) -> Generator[Event, None, None]:
        raise NotImplementedError


class EventStream(BaseEventStream):
    """Event stream protocol for building mock OpenAI server sent event stream"""

    def __iter__(self) -> Generator[bytes, None, None]:
        for _event in self.generate():
            t, d = _event.to_sse_event()
            if t:
                yield t
            if d:
                yield d

        yield b"event: done\n"
        yield b"data: [DONE]\n\n"


class AsyncEventStream(BaseEventStream):
    """Async event stream protocol for building mock OpenAI server sent event stream"""

    async def __aiter__(self) -> AsyncIterator[bytes]:
        async for _event in make_async_generator(self.generate()):
            t, d = _event.to_sse_event()
            if t:
                yield t
            if d:
                yield d
        yield b"event: done\n"
        yield b"data: [DONE]\n\n"
