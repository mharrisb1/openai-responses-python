from openai.types.beta.assistant import Assistant

from ._base import _generic_merge_with_partial

from ..._types.partials.assistants import PartialAssistant

__all__ = ["merge_assistant_with_partial"]


def merge_assistant_with_partial(a: Assistant, p: PartialAssistant) -> Assistant:
    return _generic_merge_with_partial(Assistant, a, p)
