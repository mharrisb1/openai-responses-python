import inspect
from functools import wraps
from typing import Any, Callable, Optional

import respx

from ._routes import BetaRoutes, ChatRoutes, EmbeddingsRoutes, FileRoutes, ModelRoutes
from .stores import StateStore


class OpenAIMock:
    beta: BetaRoutes
    chat: ChatRoutes
    embeddings: EmbeddingsRoutes
    files: FileRoutes
    models: ModelRoutes

    def __init__(
        self,
        base_url: Optional[str] = None,
        state: Optional[StateStore] = None,
    ) -> None:
        self._router = respx.mock(
            assert_all_called=False,
            base_url=base_url or "https://api.openai.com/v1",
        )
        self._state = state or StateStore()
        self._init_routes()

    @property
    def router(self) -> respx.MockRouter:
        """[RESPX](https://lundberg.github.io/respx) router with patched OpenAI routes"""
        return self._router

    @property
    def state(self) -> StateStore:
        """State store for API resources"""
        return self._state

    @state.setter
    def state(self, value: StateStore) -> None:
        assert isinstance(value, StateStore), "Object is not an instance of StateStore"
        self._state = value
        self._init_routes()

    def _init_routes(self) -> None:
        """Called on construction and anytime that either `router` or `state` values are changed"""
        self.beta = BetaRoutes(self._router, self._state)
        self.chat = ChatRoutes(self._router)
        self.embeddings = EmbeddingsRoutes(self._router)
        self.files = FileRoutes(self._router, self._state)
        self.models = ModelRoutes(self._router, self._state)

        # NOTE: need to sort routes to avoid match conflicts
        self._router.routes._routes.sort(key=lambda r: len(repr(r._pattern)), reverse=True)  # type: ignore

    def _start_mock(self):
        def wrapper(fn: Callable[..., Any]):
            is_async = inspect.iscoroutinefunction(fn)
            argspec = inspect.getfullargspec(fn)
            needs_ref = "openai_mock" in argspec.args

            @wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs["openai_mock"] = self
                with self.router:
                    return await fn(*args, **kwargs)

            @wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs["openai_mock"] = self
                with self.router:
                    return fn(*args, **kwargs)

            return async_wrapper if is_async else sync_wrapper

        return wrapper
