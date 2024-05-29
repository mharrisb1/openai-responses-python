from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.types import Model
from openai.pagination import SyncCursorPage

from ._base import StatefulRoute

from ..stores import StateStore
from .._types.partials.models import PartialModel
from .._types.partials.sync_cursor_page import PartialSyncCursorPage

from .._utils.serde import model_dict


class ModelListRoute(
    StatefulRoute[SyncCursorPage[Model], PartialSyncCursorPage[PartialModel]]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex="/models"),
            status_code=200,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route
        data = self._state.models.list()
        model = SyncCursorPage[Model](data=data)
        return httpx.Response(status_code=200, json=model_dict(model), request=request)

    @staticmethod
    def _build(
        partial: PartialSyncCursorPage[PartialModel],
        request: httpx.Request,
    ) -> SyncCursorPage[Model]:
        raise NotImplementedError


class ModelRetrieveRoute(StatefulRoute[Model, PartialModel]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex=r"/models/(?P<model_id>.+)"),
            status_code=200,
            state=state,
        )

    @override
    def _handler(
        self,
        request: httpx.Request,
        route: respx.Route,
        **kwargs: Any,
    ) -> httpx.Response:
        self._route = route
        model_id = kwargs["model_id"]
        found = self._state.models.get(model_id)
        if not found:
            return httpx.Response(404)

        return httpx.Response(status_code=200, json=model_dict(found), request=request)

    @staticmethod
    def _build(partial: PartialModel, request: httpx.Request) -> Model:
        raise NotImplementedError
