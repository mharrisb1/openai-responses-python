import time
from typing import Any

import httpx
import respx

from openai_responses.decorators import side_effect


def test_side_effect_decorator():
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
