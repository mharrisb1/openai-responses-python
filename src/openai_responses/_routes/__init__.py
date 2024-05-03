import respx

from .._stores import StateStore

from .chat import ChatCompletionsCreateRoute
from .embeddings import EmbeddingsCreateRoute
from .files import FileCreateRoute, FileListRoute, FileRetrieveRoute, FileDeleteRoute
from .assistants import (
    AssistantCreateRoute,
    AssistantListRoute,
    AssistantRetrieveRoute,
    AssistantUpdateRoute,
    AssistantDeleteRoute,
)
from .threads import ThreadCreateRoute

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


class BetaRoutes:
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        self.assistants = AssistantsRoutes(router, state)
        self.threads = ThreadRoutes(router, state)


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
