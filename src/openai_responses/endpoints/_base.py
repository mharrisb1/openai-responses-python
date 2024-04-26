import inspect
from functools import partial, wraps
from typing import Any, Callable, Dict, List, Optional, Protocol, TypedDict

import httpx
import respx
from faker import Faker
from faker_openai_api_provider import OpenAiApiProvider

from ..decorators import unwrap
from ..state import StateStore


class KwargsGetterProtocol(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        ...


class RouteRegistration(TypedDict):
    name: str
    method: Callable[..., respx.Route]
    pattern: Optional[str]
    side_effect: Callable[..., httpx.Response]


class Mock:
    def __init__(
        self,
        *,
        name: str,
        endpoint: Optional[str] = None,
        route_registrations: Optional[List[RouteRegistration]] = None,
    ) -> None:
        print("Mocker initialized")
        self._name = name
        self._base_url = "https://api.openai.com"
        self._endpoint = endpoint or ""
        self._registrations = route_registrations or []

        fake = Faker()
        fake.add_provider(OpenAiApiProvider)
        self._faker: OpenAiApiProvider.Api = fake.openai()

    @property
    def name(self) -> str:
        return self._name

    @property
    def base_url(self) -> str:
        return self._base_url

    def set_base_url(self, url: str) -> None:
        self._base_url = url

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @property
    def url(self) -> str:
        return self._base_url + self._endpoint

    @staticmethod
    def _sort_routes(routes: List[respx.Route]) -> None:
        routes.sort(key=lambda r: len(repr(r._pattern)), reverse=True)  # type: ignore

    def _register_routes(self, **kwargs: Any) -> None:
        for registration in self._registrations:
            setattr(
                self,
                registration["name"],
                CallContainer(
                    route=registration["method"](
                        url__regex=self.url + (registration["pattern"] or "")
                    ).mock(
                        side_effect=partial(
                            registration["side_effect"],
                            **kwargs,
                        )
                    )
                ),
            )


class StatelessMock(Mock):
    def _make_decorator(
        self,
        common_kwargs_getter: KwargsGetterProtocol,
    ):
        def decorator(fn: Callable[..., Any]):
            is_async = inspect.iscoroutinefunction(fn)
            argspec = inspect.getfullargspec(unwrap(fn))
            needs_ref = self._name in argspec.args

            @wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs[self.name] = self
                common_kwargs = common_kwargs_getter(*args, **kwargs)
                with respx.mock:
                    self._register_routes(**common_kwargs)
                    self._sort_routes(respx.mock.routes._routes)
                    return await fn(*args, **kwargs)

            @wraps(fn)
            def wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs[self.name] = self
                common_kwargs = common_kwargs_getter(*args, **kwargs)
                with respx.mock:
                    self._register_routes(**common_kwargs)
                    self._sort_routes(respx.mock.routes._routes)
                    return fn(*args, **kwargs)

            return wrapper if not is_async else async_wrapper

        return decorator


class StatefulMock(Mock):
    def _make_decorator(
        self,
        common_kwargs_getter: KwargsGetterProtocol,
        state_store: StateStore,
    ):
        def decorator(fn: Callable[..., Any]):
            is_async = inspect.iscoroutinefunction(fn)
            argspec = inspect.getfullargspec(unwrap(fn))
            needs_ref = self._name in argspec.args

            @wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs[self.name] = self
                state = kwargs.get("state_store", state_store)
                common_kwargs = common_kwargs_getter(used_state=state, *args, **kwargs)
                with respx.mock:
                    self._register_routes(**common_kwargs)
                    self._sort_routes(respx.mock.routes._routes)
                    return await fn(*args, **kwargs)

            @wraps(fn)
            def wrapper(*args: Any, **kwargs: Any):
                if needs_ref:
                    kwargs[self.name] = self
                state = kwargs.get("state_store", state_store)
                common_kwargs = common_kwargs_getter(used_state=state, *args, **kwargs)
                with respx.mock:
                    self._register_routes(**common_kwargs)
                    self._sort_routes(respx.mock.routes._routes)
                    return fn(*args, **kwargs)

            return wrapper if not is_async else async_wrapper

        return decorator


class CallContainer:
    def __init__(self, route: Optional[respx.Route] = None) -> None:
        self.route = route or respx.Route()
