from typing import Optional

import httpx

from openai.types.beta.threads.run import Run

from ._base import _generic_builder
from ..._routes.runs import RunCreateRoute
from ..._types.partials.runs import PartialRun

__all__ = ["run_from_create_request"]


def run_from_create_request(
    thread_id: str,
    request: httpx.Request,
    *,
    extra: Optional[PartialRun] = None,
) -> Run:
    partial: PartialRun = {"thread_id": thread_id}
    if extra:
        partial |= extra
    return _generic_builder(RunCreateRoute, request, partial)
