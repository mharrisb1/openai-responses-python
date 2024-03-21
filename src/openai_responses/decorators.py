import time
import warnings
from typing import Any, Callable

import httpx
import respx
from decorator import decorator


@decorator
def side_effect(fn: Callable[..., httpx.Response], *args: Any, **kwargs: Any):
    # inject latency
    latency: float = kwargs.get("latency", 0.0)
    time.sleep(latency)

    try:
        route = next((arg for arg in args if isinstance(arg, respx.Route)))
        failures: int = kwargs.get("failures", 0)
        if route.call_count < failures:
            return httpx.Response(status_code=500)
    except StopIteration:
        warnings.warn("Could not find route in side effect call")

    return fn(*args, **kwargs)
