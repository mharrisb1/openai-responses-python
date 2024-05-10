import json
from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.types.beta.threads.run import Run
from openai.types.beta.threads.run_create_params import RunCreateParams

from ._base import StatefulRoute

from .._stores import StateStore
from .._types.partials.runs import PartialRun

from .._utils.faker import faker
from .._utils.serde import model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s


__all__ = ["RunCreateRoute"]


class RunCreateRoute(StatefulRoute[Run, PartialRun]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/v1/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/runs"
            ),
            status_code=201,
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

        thread_id = kwargs["thread_id"]
        found_thread = self._state.beta.threads.get(thread_id)
        if not found_thread:
            return httpx.Response(404)

        content: RunCreateParams = json.loads(request.content)

        found_asst = self._state.beta.assistants.get(content["assistant_id"])
        if not found_asst:
            return httpx.Response(404)

        model = self._build(
            {
                "thread_id": thread_id,
                "instructions": found_asst.instructions or "",
                "model": found_asst.model,
                "tools": [model_dict(t) for t in (found_asst.tools or [])],  # type: ignore
            },
            request,
        )
        self._state.beta.threads.runs.put(model)
        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(model),
        )

    @staticmethod
    def _build(partial: PartialRun, request: httpx.Request) -> Run:
        content = json.loads(request.content)
        defaults: PartialRun = {
            "id": faker.beta.thread.run.id(),
            "created_at": utcnow_unix_timestamp_s(),
            "instructions": "",
            "object": "thread.run",
            "status": "queued",
        }
        return model_parse(Run, defaults | partial | content)