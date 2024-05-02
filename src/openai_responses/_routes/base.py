from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Union

import httpx
import respx

from openai import BaseModel

from .._stores import StateStore
from .._types.generics import M, P
from .._types.protocols import ResponseHandler
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
        self._response: Optional[Union[httpx.Response, M, P, ResponseHandler]] = None

    @property
    def calls(self):
        return self._route.calls

    @property
    def response(self) -> Optional[Union[httpx.Response, M, P, ResponseHandler]]:
        return self._handler

    @response.setter
    def response(self, value: Union[httpx.Response, M, P, ResponseHandler]) -> None:
        self._response = value
        self._route.side_effect = self._side_effect

    @property
    def _side_effect(self) -> ResponseHandler:
        handler = self._response or self._handler
        if callable(handler):
            return handler

        def _handler(request: httpx.Request, route: respx.Route, **kwargs: Any):
            if isinstance(handler, BaseModel):
                return httpx.Response(
                    status_code=self._status_code,
                    json=model_dict(handler),
                )

            elif isinstance(handler, httpx.Response):
                return handler

            else:
                return httpx.Response(
                    status_code=self._status_code,
                    json=model_dict(self._build(handler, request)),
                )

        return _handler

    @abstractmethod
    def _handler(
        self,
        request: httpx.Request,
        route: respx.Route,
        **kwargs: Any,
    ) -> httpx.Response:
        """Default response handler for route

        Args:
            request (httpx.Request): User request
            route (respx.Route): Associated route

        Returns:
            httpx.Response: Mocked response
        """
        raise NotADirectoryError

    @staticmethod
    @abstractmethod
    def _build(partial: P, request: httpx.Request) -> M:
        """Merge partial and content to create a ful instance of model M

        Args:
            partial (P): Partial model
            content (bytes): Request content serializable to JSON

        Returns:
            M: Full model instance
        """
        raise NotImplementedError


class StatelessRoute(Route[M, P]):
    pass


class StatefulRoute(Route[M, P]):
    def __init__(self, route: respx.Route, status_code: int, state: StateStore) -> None:
        super().__init__(route, status_code)
        self._state = state
