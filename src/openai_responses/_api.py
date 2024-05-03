from typing import Optional

from ._mock import OpenAIMock
from ._stores import StateStore


def mock(
    *,
    base_url: Optional[str] = None,
    state: Optional[StateStore] = None,
):
    openai_mock = OpenAIMock(base_url, state)
    return openai_mock._start_mock()
