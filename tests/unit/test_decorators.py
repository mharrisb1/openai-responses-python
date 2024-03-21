import time
from typing import Any

import httpx
import respx

from openai_responses.decorators import side_effect, unwrap


def test_side_effect_make_decorator():
    @side_effect
    def wrapped_side_effect(route: respx.Route, **kwargs: Any) -> httpx.Response:
        return httpx.Response(status_code=200)

    res = wrapped_side_effect(respx.Route())
    assert res.status_code == 200

    res = wrapped_side_effect(respx.Route(), failures=2)
    assert res.status_code == 500

    t1 = time.time()
    res = wrapped_side_effect(respx.Route(), latency=1)
    t2 = time.time()
    assert res.status_code == 200
    assert (t2 - t1) > 1


def test_unwrap():
    global i
    i = 0

    def foo_decorator(func: Any):
        def wrapper():
            global i
            i += 1
            return func()

        return wrapper

    @foo_decorator
    @foo_decorator
    def my_function():
        global i
        i += 1
        return i

    assert my_function() == 3

    i = 0

    original = unwrap(my_function)

    assert original() == 1
