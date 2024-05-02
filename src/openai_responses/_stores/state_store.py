from typing import Dict, Generic, List, Literal, Optional, TypeVar, Union

from openai.types import FileObject
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.message import Message
from openai.types.beta.threads.run import Run
from openai.types.beta.threads.runs.run_step import RunStep


__all__ = ["StateStore"]

M = TypeVar(
    "M",
    bound=Union[
        FileObject,
        Assistant,
        Thread,
        Message,
        Run,
        RunStep,
    ],
)


class StateStore:
    def __init__(self) -> None:
        self.files = FileStore()
        self.beta = Beta()


class Beta:
    def __init__(self) -> None:
        self.assistants = AssistantStore()
        self.threads = ThreadStore()


class BaseStore(Generic[M]):
    def __init__(self) -> None:
        self._data: Dict[str, M] = {}

    def put(self, obj: M) -> None:
        self._data[obj.id] = obj

    def get(self, id: str) -> Optional[M]:
        return self._data.get(id)

    def delete(self, id: str) -> bool:
        if self._data.get(id):
            del self._data[id]
            return True
        else:
            return False


# TODO: add content storage
class FileStore(BaseStore[FileObject]):
    def list(
        self,
        purpose: Optional[
            Literal[
                "fine-tune",
                "fine-tune-results",
                "assistants",
                "assistants_output",
            ]
        ] = None,
    ) -> List[FileObject]:
        files = list(self._data.values())
        if purpose:
            files = [file for file in files if file.purpose == purpose]
        return files


class AssistantStore(BaseStore[Assistant]):
    def list(
        self,
        limit: Optional[int] = None,
        order: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> List[Assistant]:
        objs = list(self._data.values())
        objs = list(reversed(objs)) if (order or "desc") == "desc" else objs

        start_ix = 0
        if after:
            obj = self._data.get(after)
            if obj:
                start_ix = objs.index(obj) + 1

        end_ix = None
        if before:
            obj = self._data.get(before)
            if obj:
                end_ix = objs.index(obj)

        objs = objs[start_ix:end_ix]
        return objs[: (limit or 20) + 1]


class ThreadStore(BaseStore[Thread]):
    def __init__(self) -> None:
        super().__init__()
        self.messages = MessageStore()
        self.runs = RunStore()


class MessageStore(BaseStore[Message]):
    def list(
        self,
        thread_id: str,
        limit: Optional[int] = None,
        order: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> List[Message]:
        objs = [m for m in list(self._data.values()) if m.thread_id == thread_id]
        objs = list(reversed(objs)) if (order or "desc") == "desc" else objs

        start_ix = 0
        if after:
            obj = self._data.get(after)
            if obj:
                start_ix = objs.index(obj) + 1

        end_ix = None
        if before:
            obj = self._data.get(before)
            if obj:
                end_ix = objs.index(obj)

        objs = objs[start_ix:end_ix]
        return objs[: (limit or 20) + 1]


class RunStore(BaseStore[Run]):
    def __init__(self) -> None:
        super().__init__()
        self.steps = RunStepStore()

    def list(
        self,
        thread_id: str,
        limit: Optional[int] = None,
        order: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> List[Run]:
        objs = [m for m in list(self._data.values()) if m.thread_id == thread_id]
        objs = list(reversed(objs)) if (order or "desc") == "desc" else objs

        start_ix = 0
        if after:
            obj = self._data.get(after)
            if obj:
                start_ix = objs.index(obj) + 1

        end_ix = None
        if before:
            obj = self._data.get(before)
            if obj:
                end_ix = objs.index(obj)

        objs = objs[start_ix:end_ix]
        return objs[: (limit or 20) + 1]


class RunStepStore(BaseStore[RunStep]):
    def list(
        self,
        thread_id: str,
        run_id: str,
        limit: Optional[int] = None,
        order: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> List[RunStep]:
        objs = [
            m
            for m in list(self._data.values())
            if m.thread_id == thread_id and m.run_id == run_id
        ]
        objs = list(reversed(objs)) if (order or "desc") == "desc" else objs

        start_ix = 0
        if after:
            obj = self._data.get(after)
            if obj:
                start_ix = objs.index(obj) + 1

        end_ix = None
        if before:
            obj = self._data.get(before)
            if obj:
                end_ix = objs.index(obj)

        objs = objs[start_ix:end_ix]
        return objs[: (limit or 20) + 1]
