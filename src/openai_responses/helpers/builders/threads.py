from typing import Optional

import httpx

from openai.types.beta.thread import Thread

from ._base import _generic_builder
from ..._routes.threads import ThreadCreateRoute
from ..._types.partials.threads import PartialThread

__all__ = ["thread_from_create_request"]


def thread_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialThread] = None,
) -> Thread:
    return _generic_builder(ThreadCreateRoute, request, extra)
