from typing import Any, Protocol

import httpx
import respx


class ResponseHandler(Protocol):
    def __call__(
        self,
        request: httpx.Request,
        route: respx.Route,
        **kwargs: Any,
    ) -> httpx.Response: ...
