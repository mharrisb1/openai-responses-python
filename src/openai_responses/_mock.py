import inspect
from functools import wraps
from typing import Any, Callable, Optional

import respx

from ._routes import ChatWrapper


class OpenAIMock:
    def __init__(self) -> None:
        self._router: Optional[respx.MockRouter] = None

    def __call__(self, *, base_url: Optional[str] = None):
        self._router = respx.mock(
            assert_all_called=False,
            base_url=base_url or "https://api.openai.com",
        )

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
                    # TODO: init state store
                    self._register_routes()
                    return await fn(*args, **kwargs)

            @wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs["openai_mock"] = self
                assert self._router is not None
                with self._router:
                    # TODO: init state store
                    self._register_routes()
                    return fn(*args, **kwargs)

            return async_wrapper if is_async else sync_wrapper

        return wrapper

    def _register_routes(self) -> None: ...

    @property
    def chat(self) -> ChatWrapper:
        assert self._router is not None, "Can only be called within a mock"
        return ChatWrapper(self._router)
