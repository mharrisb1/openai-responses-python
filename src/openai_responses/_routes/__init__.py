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
from .moderation import ModerationCreateRoute

from .beta import BetaRoutes

from .beta.vector_stores import (
    VectorStoreCreateRoute,
    VectorStoreListRoute,
    VectorStoreRetrieveRoute,
    VectorStoreUpdateRoute,
    VectorStoreDeleteRoute,
)
from .beta.vector_store_files import (
    VectorStoreFileCreateRoute,
    VectorStoreFileListRoute,
    VectorStoreFileRetrieveRoute,
    VectorStoreFileDeleteRoute,
)
from .beta.vector_store_file_batches import (
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
    "ModelRoutes",
    "ModerationsRoutes",
    "VectorStoreRoutes",
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


class ModerationsRoutes:
    def __init__(self, router: respx.MockRouter) -> None:
        self.create = ModerationCreateRoute(router)


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
