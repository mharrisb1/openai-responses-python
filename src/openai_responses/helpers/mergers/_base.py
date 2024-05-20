from typing import Any, Mapping, Type
from ..._types.generics import M
from ..._utils.serde import model_dict, model_parse

__all__ = ["_generic_merge_with_partial"]


def _generic_merge_with_partial(t: Type[M], m: M, p: Mapping[str, Any]) -> M:
    merged = model_dict(m) | dict(p)
    return model_parse(t, merged)
