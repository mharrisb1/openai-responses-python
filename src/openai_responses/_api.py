from typing import Optional

from ._mock import OpenAIMock
from ._stores import StateStore


def mock(
    *,
    base_url: Optional[str] = None,
    state: Optional[StateStore] = None,
):
    """
    Args:
        base_url (Optional[str], optional): Override base URL. Defaults to None.
        state (Optional[StateStore], optional): Override default empty state. Defaults to None.
    """
    openai_mock = OpenAIMock(base_url, state)
    return openai_mock._start_mock()
