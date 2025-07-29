import threading
from contextvars import ContextVar
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .effect import EffectWrapper

# --- 1. 定义线程局部和上下文变量来存储当前的 effect ---
_thread_local_current_effect = threading.local()
_async_local_current_effect: ContextVar[Optional['EffectWrapper']] = ContextVar('async_local_current_effect', default=None)

