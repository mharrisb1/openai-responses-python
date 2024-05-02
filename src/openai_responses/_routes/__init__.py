import respx

from .._stores import StateStore

from .chat import ChatCompletionsCreateRoute
from .embeddings import EmbeddingsCreateRoute
from .files import FileCreateRoute

__all__ = [
    "ChatWrapper",
    "EmbeddingsWrapper",
    "FileWrapper",
]


class ChatWrapper:
    def __init__(self, router: respx.MockRouter) -> None:
        self.completions = ChatCompletionWrapper(router)


class ChatCompletionWrapper:
    def __init__(self, router: respx.MockRouter) -> None:
        self.create = ChatCompletionsCreateRoute(router)


class EmbeddingsWrapper:
    def __init__(self, router: respx.MockRouter) -> None:
        self.create = EmbeddingsCreateRoute(router)


class FileWrapper:
    def __init__(self, router: respx.MockRouter, store: StateStore) -> None:
        self.create = FileCreateRoute(router, store)
