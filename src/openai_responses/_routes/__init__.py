import respx

from ..stores import StateStore

from .chat import ChatCompletionsCreateRoute
from .embeddings import EmbeddingsCreateRoute
from .files import (
    FileCreateRoute,
    FileListRoute,
    FileRetrieveRoute,
    FileDeleteRoute,
    FileRetrieveContentRoute,
)
from .models import ModelListRoute, ModelRetrieveRoute
from .assistants import (
    AssistantCreateRoute,
    AssistantListRoute,
    AssistantRetrieveRoute,
    AssistantUpdateRoute,
    AssistantDeleteRoute,
)
from .threads import (
    ThreadCreateRoute,
    ThreadRetrieveRoute,
    ThreadUpdateRoute,
    ThreadDeleteRoute,
)
from .messages import (
    MessageCreateRoute,
    MessageListRoute,
    MessageRetrieveRoute,
    MessageUpdateRoute,
    MessageDeleteRoute,
)
from .runs import (
    RunCreateRoute,
    ThreadCreateAndRun,
    RunListRoute,
    RunRetrieveRoute,
    RunUpdateRoute,
    RunSubmitToolOutputsRoute,
    RunCancelRoute,
)
from .run_steps import RunStepListRoute, RunStepRetrieveRoute
from .vector_stores import (
    VectorStoreCreateRoute,
    VectorStoreListRoute,
    VectorStoreRetrieveRoute,
    VectorStoreUpdateRoute,
    VectorStoreDeleteRoute,
)
from .vector_store_files import (
    VectorStoreFileCreateRoute,
    VectorStoreFileListRoute,
    VectorStoreFileRetrieveRoute,
    VectorStoreFileDeleteRoute,
)
from .vector_store_file_batches import (
    VectorStoreFileBatchCreateRoute,
    VectorStoreFileBatchRetrieveRoute,
    VectorStoreFileBatchCancelRoute,
    VectorStoreFileBatchListFilesRoute,
)

__all__ = [
    "BetaRoutes",
    "ChatRoutes",
    "EmbeddingsRoutes",
    "FileRoutes",
]


class ChatRoutes:
    def __init__(self, router: respx.MockRouter) -> None:
        self.completions = ChatCompletionRoutes(router)


class ChatCompletionRoutes:
    def __init__(self, router: respx.MockRouter) -> None:
        self.create = ChatCompletionsCreateRoute(router)


class EmbeddingsRoutes:
    def __init__(self, router: respx.MockRouter) -> None:
        self.create = EmbeddingsCreateRoute(router)


class FileRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.create = FileCreateRoute(router, state)
        self.list = FileListRoute(router, state)
        self.retrieve = FileRetrieveRoute(router, state)
        self.delete = FileDeleteRoute(router, state)
        self.content = FileRetrieveContentRoute(router, state)


class ModelRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.list = ModelListRoute(router, state)
        self.retrieve = ModelRetrieveRoute(router, state)


class BetaRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.assistants = AssistantsRoutes(router, state)
        self.threads = ThreadRoutes(router, state)
        self.vector_stores = VectorStoreRoutes(router, state)


class AssistantsRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.create = AssistantCreateRoute(router, state)
        self.list = AssistantListRoute(router, state)
        self.retrieve = AssistantRetrieveRoute(router, state)
        self.update = AssistantUpdateRoute(router, state)
        self.delete = AssistantDeleteRoute(router, state)


class ThreadRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.create = ThreadCreateRoute(router, state)
        self.retrieve = ThreadRetrieveRoute(router, state)
        self.update = ThreadUpdateRoute(router, state)
        self.delete = ThreadDeleteRoute(router, state)
        self.create_and_run = ThreadCreateAndRun(router, state)

        self.messages = MessageRoutes(router, state)
        self.runs = RunRoutes(router, state)


class MessageRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.create = MessageCreateRoute(router, state)
        self.list = MessageListRoute(router, state)
        self.retrieve = MessageRetrieveRoute(router, state)
        self.update = MessageUpdateRoute(router, state)
        self.delete = MessageDeleteRoute(router, state)


class RunRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.create = RunCreateRoute(router, state)
        self.list = RunListRoute(router, state)
        self.retrieve = RunRetrieveRoute(router, state)
        self.update = RunUpdateRoute(router, state)
        self.submit_tool_outputs = RunSubmitToolOutputsRoute(router, state)
        self.cancel = RunCancelRoute(router, state)

        self.steps = RunStepRoutes(router, state)


class RunStepRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.list = RunStepListRoute(router, state)
        self.retrieve = RunStepRetrieveRoute(router, state)


class VectorStoreRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.create = VectorStoreCreateRoute(router, state)
        self.list = VectorStoreListRoute(router, state)
        self.retrieve = VectorStoreRetrieveRoute(router, state)
        self.update = VectorStoreUpdateRoute(router, state)
        self.delete = VectorStoreDeleteRoute(router, state)

        self.files = VectorStoreFileRoutes(router, state)
        self.file_batches = VectorStoreFileBatchRoutes(router, state)


class VectorStoreFileRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.create = VectorStoreFileCreateRoute(router, state)
        self.list = VectorStoreFileListRoute(router, state)
        self.retrieve = VectorStoreFileRetrieveRoute(router, state)
        self.delete = VectorStoreFileDeleteRoute(router, state)


class VectorStoreFileBatchRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.create = VectorStoreFileBatchCreateRoute(router, state)
        self.retrieve = VectorStoreFileBatchRetrieveRoute(router, state)
        self.cancel = VectorStoreFileBatchCancelRoute(router, state)
        self.list_files = VectorStoreFileBatchListFilesRoute(router, state)
