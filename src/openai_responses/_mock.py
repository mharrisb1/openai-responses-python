import inspect
from functools import wraps
from typing import Any, Callable, Optional

import respx

from ._routes import ChatWrapper, EmbeddingsWrapper, FileWrapper
from ._stores import StateStore

ASSERTION_ERROR = "Can only be called within a mock context"


class OpenAIMock:
    def __init__(self) -> None:
        self._router: Optional[respx.MockRouter] = None
        self._state: Optional[StateStore] = None

    def __call__(
        self,
        *,
        base_url: Optional[str] = None,
        state: Optional[StateStore] = None,
    ):
        self._router = respx.mock(
            assert_all_called=False,
            base_url=base_url or "https://api.openai.com",
        )

        self._state = state or StateStore()

        def wrapper(fn: Callable[..., Any]):
            is_async = inspect.iscoroutinefunction(fn)
            argspec = inspect.getfullargspec(fn)
            needs_ref = "openai_mock" in argspec.args

            @wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs["openai_mock"] = self
                assert self._router is not None
                with self._router:
                    return await fn(*args, **kwargs)

            @wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs["openai_mock"] = self
                assert self._router is not None
                with self._router:
                    return fn(*args, **kwargs)

            return async_wrapper if is_async else sync_wrapper

        return wrapper

    @property
    def chat(self) -> ChatWrapper:
        assert self._router, ASSERTION_ERROR
        return ChatWrapper(self._router)

    @property
    def embeddings(self) -> EmbeddingsWrapper:
        assert self._router, ASSERTION_ERROR
        return EmbeddingsWrapper(self._router)

    @property
    def files(self) -> FileWrapper:
        assert self._router and self._state, ASSERTION_ERROR
        return FileWrapper(self._router, self._state)
