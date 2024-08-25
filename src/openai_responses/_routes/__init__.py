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

__all__ = [
    "BetaRoutes",
    "ChatRoutes",
    "EmbeddingsRoutes",
    "FileRoutes",
    "ModelRoutes",
    "ModerationsRoutes",
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
