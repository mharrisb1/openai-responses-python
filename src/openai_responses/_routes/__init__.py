import respx

from .chat import ChatCompletionsCreateRoute
from .embeddings import EmbeddingsCreateRoute

__all__ = [
    "ChatWrapper",
    "EmbeddingsWrapper",
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
