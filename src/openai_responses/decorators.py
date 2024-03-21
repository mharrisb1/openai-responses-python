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


def unwrap(wrapped: Callable[..., Any]) -> Callable[..., Any]:
    """
    https://stackoverflow.com/a/77694433
    """
    closure = wrapped.__closure__
    if closure:
        for cell in closure:
            if hasattr(cell.cell_contents, "__module__"):
                if cell.cell_contents.__module__.split(".")[0] == "openai_responses":
                    continue
            if hasattr(cell.cell_contents, "__closure__"):
                return (
                    cell.cell_contents
                    if cell.cell_contents.__closure__ is None
                    else unwrap(cell.cell_contents)
                )
    return wrapped
