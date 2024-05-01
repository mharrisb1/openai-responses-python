import respx

from .chat import ChatCompletionsCreateRoute

__all__ = [
    "ChatWrapper",
]


class ChatWrapper:
    def __init__(self, router: respx.MockRouter) -> None:
        self.completions = ChatCompletionWrapper(router)


class ChatCompletionWrapper:
    def __init__(self, router: respx.MockRouter) -> None:
        self.create = ChatCompletionsCreateRoute(router)
