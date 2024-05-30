from openai.types.beta.thread import Thread

from ._base import _generic_merge_with_partial

from ..._types.partials.threads import PartialThread

__all__ = ["merge_thread_with_partial"]


def merge_thread_with_partial(t: Thread, p: PartialThread) -> Thread:
    return _generic_merge_with_partial(Thread, t, p)
