from typing import Optional, Type

import httpx

from ..._routes._base import Route
from ..._types.generics import M, P

__all__ = ["_generic_builder"]


def _generic_builder(
    route: Type[Route[M, P]],
    request: httpx.Request,
    extra: Optional[P] = None,
) -> M:
    return getattr(route, "_build")(extra or {}, request)
