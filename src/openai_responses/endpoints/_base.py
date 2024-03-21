import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Protocol

import httpx
import respx
from faker import Faker
from faker_openai_api_provider import OpenAiApiProvider

from ..state import StateStore


class KwargsGetterProtocol(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]: ...


class Mock(ABC):
    BASE_URL = "https://api.openai.com/v1"

    def __init__(self) -> None:
        _fake = Faker()
        _fake.add_provider(OpenAiApiProvider)
        self._faker: OpenAiApiProvider.Api = _fake.openai()

    @abstractmethod
    def _register_routes(self, **common: Any) -> None: ...


class StatelessMock(Mock):
    def __call__(
        self,
        mocker_class: str,
        common_kwargs_getter: KwargsGetterProtocol,
    ):
        def decorator(fn: Callable[..., Any]):
            is_async = inspect.iscoroutinefunction(fn)
            argspec = inspect.getfullargspec(fn)
            needs_ref = mocker_class in argspec.args

            async def async_wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs[mocker_class] = self
                common_kwargs = common_kwargs_getter(*args, **kwargs)
                with respx.mock:
                    self._register_routes(**common_kwargs)
                    return await fn(*args, **kwargs)

            def wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs[mocker_class] = self
                common_kwargs = common_kwargs_getter(*args, **kwargs)
                with respx.mock:
                    self._register_routes(**common_kwargs)
                    return fn(*args, **kwargs)

            return wrapper if not is_async else async_wrapper

        return decorator


class StatefulMock(Mock):

    def __call__(
        self,
        mocker_class: str,
        common_kwargs_getter: KwargsGetterProtocol,
        state_store: StateStore,
    ):
        def decorator(fn: Callable[..., Any]):
            is_async = inspect.iscoroutinefunction(fn)
            argspec = inspect.getfullargspec(fn)
            needs_ref = mocker_class in argspec.args

            async def async_wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs[mocker_class] = self
                state = kwargs.get("state_store", state_store)
                common_kwargs = common_kwargs_getter(used_state=state, *args, **kwargs)
                with respx.mock:
                    self._register_routes(**common_kwargs)
                    return await fn(*args, **kwargs)

            def wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs[mocker_class] = self
                state = kwargs.get("state_store", state_store)
                common_kwargs = common_kwargs_getter(used_state=state, *args, **kwargs)
                with respx.mock:
                    self._register_routes(**common_kwargs)
                    return fn(*args, **kwargs)

            return wrapper if not is_async else async_wrapper

        return decorator


class CallContainer:
    def __init__(self) -> None:
        self.route = respx.Route()
        self.request: Optional[httpx.Request] = None
        self.response: Optional[httpx.Response] = None
