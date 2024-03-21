import datetime as dt
from typing import Any, Optional, Type, TypeVar

from openai import BaseModel

M = TypeVar("M", bound=BaseModel)


def utcnow_unix_timestamp_s() -> int:
    return int(dt.datetime.now().timestamp())


def model_dict(m: BaseModel) -> dict[str, Any]:
    if hasattr(m, "model_dump"):
        return getattr(m, "model_dump")()
    else:
        return getattr(m, "dict")()


def model_parse(m: Type[M], d: Optional[object]) -> Optional[M]:
    if not d:
        return None
    if hasattr(m, "model_validate"):
        return getattr(m, "model_validate")(d)
    else:
        return getattr(m, "parse_obj")(d)
