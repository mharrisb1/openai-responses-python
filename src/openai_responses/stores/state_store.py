from typing import Dict, Generic, List, Literal, Optional, TypeVar, Union

from openai.types import FileObject, Model
from openai.types.beta.vector_store import VectorStore
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.message import Message
from openai.types.beta.threads.run import Run
from openai.types.beta.threads.runs.run_step import RunStep

from .content_store import ContentStore
from .._constants import SYSTEM_MODELS
from .._utils.serde import model_parse

__all__ = ["StateStore"]

AnyModel = Union[
    FileObject,
    Assistant,
    Thread,
    Message,
    Run,
    RunStep,
    Model,
    VectorStore,
]


M = TypeVar("M", bound=AnyModel)


class StateStore:
    def __init__(self) -> None:
        self.files = FileStore()
        self.models = ModelStore()
        self.beta = Beta()

    def _blind_put(self, resource: AnyModel) -> None:
        if isinstance(resource, FileObject):
            self.files.put(resource)
        elif isinstance(resource, Assistant):
            self.beta.assistants.put(resource)
        elif isinstance(resource, Thread):
            self.beta.threads.put(resource)
        elif isinstance(resource, Message):
            self.beta.threads.messages.put(resource)
        elif isinstance(resource, Run):
            self.beta.threads.runs.put(resource)
        elif isinstance(resource, RunStep):
            self.beta.threads.runs.steps.put(resource)
        elif isinstance(resource, Model):
            self.models.put(resource)
        else:
            raise TypeError(f"Cannot put object of type {type(resource)} in store")


class Beta:
    def __init__(self) -> None:
        self.assistants = AssistantStore()
        self.threads = ThreadStore()
        self.vector_stores = VectorStoreStore()


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


class FileStore(BaseStore[FileObject]):
    def __init__(self) -> None:
        super().__init__()
        self.content = ContentStore()

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


class ModelStore(BaseStore[Model]):
    def __init__(self) -> None:
        super().__init__()
        for model in SYSTEM_MODELS:
            self._data[str(model["id"])] = model_parse(Model, model)

    def list(self) -> List[Model]:
        return list(self._data.values())


class AssistantStore(BaseStore[Assistant]):
    def list(
        self,
        limit: Optional[str] = None,
        order: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> List[Assistant]:
        limit = limit or "20"
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
        return objs[: int(limit)]


class ThreadStore(BaseStore[Thread]):
    def __init__(self) -> None:
        super().__init__()
        self.messages = MessageStore()
        self.runs = RunStore()


class MessageStore(BaseStore[Message]):
    def list(
        self,
        thread_id: str,
        limit: Optional[str] = None,
        order: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> List[Message]:
        limit = limit or "20"
        objs = [m for m in list(self._data.values()) if m.thread_id == thread_id]
        if run_id:
            objs = [obj for obj in objs if obj.run_id == run_id]
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
        return objs[: int(limit)]


class RunStore(BaseStore[Run]):
    def __init__(self) -> None:
        super().__init__()
        self.steps = RunStepStore()

    def list(
        self,
        thread_id: str,
        limit: Optional[str] = None,
        order: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> List[Run]:
        limit = limit or "20"
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
        return objs[: int(limit)]


class RunStepStore(BaseStore[RunStep]):
    def list(
        self,
        thread_id: str,
        run_id: str,
        limit: Optional[str] = None,
        order: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> List[RunStep]:
        limit = limit or "20"
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
        return objs[: int(limit)]


class VectorStoreStore(BaseStore[VectorStore]):
    def list(
        self,
        limit: Optional[str] = None,
        order: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> List[VectorStore]:
        raise NotImplementedError
