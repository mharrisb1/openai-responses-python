from abc import ABC, abstractmethod
from functools import partial
import inspect
from typing import Any, Callable, Generic, Union
from typing_extensions import override

import httpx
import respx

from openai import BaseModel

from ..stores import StateStore
from .._types.generics import M, P
from .._utils.serde import model_dict

__all__ = ["StatelessRoute", "StatefulRoute"]


class Route(ABC, Generic[M, P]):
    def __init__(
        self,
        route: respx.Route,
        status_code: int,
    ) -> None:
        self._route = route
        self._status_code = status_code
        self._response: Union[httpx.Response, M, P, Callable[..., httpx.Response]] = (
            self._handler
        )
        self._route.side_effect = self._response

    @property
    def route(self) -> respx.Route:
        return self._route

    @property
    def response(self) -> Union[httpx.Response, M, P, Callable[..., httpx.Response]]:
        return self._response

    @response.setter
    def response(
        self,
        value: Union[httpx.Response, M, P, Callable[..., httpx.Response]],
    ) -> None:
        """
        Sets the value of route response. See docs for more details and examples.

        Args:
            value: Either an HTTPX response, an OpenAI model, a partial model, or a callable that returns an HTTPX response
        """
        self._response = value
        self._route.side_effect = self._side_effect

    @property
    def _side_effect(self) -> Callable[..., httpx.Response]:
        if callable(self._response):
            return self._response

        def _handler(request: httpx.Request, route: respx.Route, **kwargs: Any):
            if isinstance(self._response, BaseModel):
                return httpx.Response(
                    status_code=self._status_code,
                    json=model_dict(self._response),
                )

            elif isinstance(self._response, httpx.Response):
                return self._response

            else:
                assert not callable(self._response)
                return httpx.Response(
                    status_code=self._status_code,
                    json=model_dict(self._build(self._response, request)),
                )

        return _handler

    def _handler(
        self,
        request: httpx.Request,
        route: respx.Route,
    ) -> httpx.Response:
        """Default response handler for route

        Args:
            request (httpx.Request): User request
            route (respx.Route): Associated route

        Returns:
            httpx.Response: Mocked response
        """
        self._route = route
        empty: Any = {}  # NOTE: avoids mypy complaint
        model = self._build(empty, request)
        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(model),
        )

    @staticmethod
    @abstractmethod
    def _build(partial: P, request: httpx.Request) -> M:
        """Merge partial and content to create a full instance of model M

        Args:
            partial (P): Partial model
            content (bytes): Request content serializable to JSON

        Returns:
            M: Full model instance
        """
        raise NotImplementedError


class StatelessRoute(Route[M, P]):
    def __init__(self, *, route: respx.Route, status_code: int) -> None:
        super().__init__(route, status_code)


class StatefulRoute(Route[M, P]):
    def __init__(
        self,
        *,
        route: respx.Route,
        status_code: int,
        state: StateStore,
    ) -> None:
        super().__init__(route, status_code)
        self._state = state

    @property
    @override
    def _side_effect(self) -> Callable[..., httpx.Response]:
        if callable(self._response):
            argspec = inspect.getfullargspec(self._response)
            needs_store = (
                "state_store" in argspec.args or "state_store" in argspec.kwonlyargs
            )
            if needs_store:
                return partial(self._response, state_store=self._state)
            else:
                return self._response

        def _handler(request: httpx.Request, route: respx.Route, **kwargs: Any):
            if isinstance(self._response, BaseModel):
                self._state._blind_put(self._response)
                return httpx.Response(
                    status_code=self._status_code,
                    json=model_dict(self._response),
                )

            elif isinstance(self._response, httpx.Response):
                return self._response

            else:
                assert not callable(self._response)
                try:
                    model = self._build(self._response, request)
                    self._state._blind_put(model)
                    return httpx.Response(
                        status_code=self._status_code,
                        json=model_dict(model),
                    )
                except NotImplementedError:
                    import warnings

                    warnings.warn("Failed to build model")
                    warnings.warn("Falling back to default handler")
                    return self._handler(request, route)

        return _handler
