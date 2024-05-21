from typing import Any, Awaitable, Callable, Optional, Union

from ._mock import OpenAIMock
from .stores import StateStore

WrappedFn = Callable[..., Union[Callable[..., Any], Awaitable[Callable[..., Any]]]]


def mock(
    *,
    base_url: Optional[str] = None,
    state: Optional[StateStore] = None,
) -> WrappedFn:
    """
    Args:
        base_url (Optional[str], optional): Override base URL. Defaults to None.
        state (Optional[StateStore], optional): Override default empty state. Defaults to None.
    """
    openai_mock = OpenAIMock(base_url, state)
    return openai_mock._start_mock()
