import inspect
from functools import wraps
from typing import Any, Callable, Optional

import respx

from ._routes import ChatWrapper, EmbeddingsWrapper, FileWrapper
from ._stores import StateStore

ASSERTION_ERROR = "Can only be called within a mock context"


class OpenAIMock:
    def __init__(
        self,
        base_url: Optional[str] = None,
        state: Optional[StateStore] = None,
    ) -> None:
        self._router = respx.mock(
            assert_all_called=False,
            base_url=base_url or "https://api.openai.com",
        )
        self._state = state or StateStore()

        self.chat = ChatWrapper(self._router)
        self.embeddings = EmbeddingsWrapper(self._router)
        self.files = FileWrapper(self._router, self._state)

        # sort routes (IMPORTANT)
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
