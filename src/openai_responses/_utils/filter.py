from typing import List, Optional, TypeVar

T = TypeVar("T")


def remove_none(ls: List[Optional[T]]) -> List[T]:
    return [el for el in ls if el]
