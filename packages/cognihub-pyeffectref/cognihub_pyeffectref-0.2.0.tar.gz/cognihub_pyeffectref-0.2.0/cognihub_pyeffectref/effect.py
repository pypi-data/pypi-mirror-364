"""EffectWrapper 类和 effect 装饰器的实现。
提供了对同步和异步效果的支持,并允许在 Ref 变化时触发效果。

用法:
    from cognihub_pyeffectref import effect, Ref
    a = Ref(1)
    b = Ref(2)
    @effect
    def my_effect(c:int)-> int:
        # 这里是效果的逻辑
        print(f"Effect triggered with value: a:{a.value} b:{b.value} c:{c}")
        return a.value + b.value + c
"""
import asyncio
import cognihub_pyeffectref.local as local
from typing import Callable, Any


class EffectWrapper:
    """
    封装 effect 函数,提供 __call__ 使其可调用,并管理其 stop 行为。
    """

    def __init__(self, func: Callable[..., Any], is_async: bool):
        self._func = func
        self.__name__ = func.__name__  # 保留原函数名
        self._is_async = is_async
        self._is_active = True
        self._last_args: tuple[Any, ...] = ()  # 保存上次调用时的位置参数
        self._last_kwargs: dict[str, Any] = {} # 保存上次调用时的关键字参数
        self._has_been_called_at_least_once = False # 标记是否至少被手动调用过一次


    # 这是effect实例被直接调用时（例如 my_effect(arg1, arg2)）的入口
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self._is_active:
            print(f"Warning: Calling inactive effect '{self.name}'.")
            return

        # 核心修改: 保存这次调用传入的参数
        self._last_args = args
        self._last_kwargs = kwargs
        self._has_been_called_at_least_once = True
        # 在__call__中进行依赖收集的上下文设置
        if self._is_async:
            return self._run_async_context(*args, **kwargs)
        else:
            return self._run_sync_context(*args, **kwargs)

    def _run_sync_context(self, *args: Any, **kwargs: Any) -> Any:
        old_effect = getattr(local._thread_local_current_effect, 'value', None)
        local._thread_local_current_effect.value = self # 设置线程局部变量为自身实例

        try:
            return self._func(*args, **kwargs) # 传递所有传入__call__的参数
        finally:
            local._thread_local_current_effect.value = old_effect

    async def _run_async_context(self, *args: Any, **kwargs: Any) -> Any:
        token = local._async_local_current_effect.set(self) # 设置 contextvar 为自身实例
        try:
            return await self._func(*args, **kwargs) # 传递所有传入__call__的参数
        finally:
            local._async_local_current_effect.reset(token)

    def run_triggered_effect(self, new_value: Any, old_value: Any) -> Any: # 接收 new_value, old_value 但通常不直接传递给 _func
        if not self._is_active:
            return
        
        # 只有在至少被手动调用过一次并保存了参数后,Ref 触发时才重用这些参数
        if not self._has_been_called_at_least_once:
            print(f"Warning: Effect '{self.name}' triggered by Ref change but never explicitly called with parameters. Skipping execution.")
            return

        # 核心修正: 使用上次保存的参数来调用 _func
        if self._is_async:
            # 对于异步函数,返回协程对象,由调用者决定如何处理
            return self._run_triggered_async(self._last_args, self._last_kwargs)
        else:
            return self._run_triggered_sync(self._last_args, self._last_kwargs)

    def _run_triggered_sync(self, args_to_pass: tuple[Any, ...], kwargs_to_pass: dict[str, Any]) -> Any:
        # 不设置上下文变量,因为依赖已收集
        return self._func(*args_to_pass, **kwargs_to_pass)

    async def _run_triggered_async(self, args_to_pass: tuple[Any, ...], kwargs_to_pass: dict[str, Any]) -> Any:
        # 不设置上下文变量,因为依赖已收集
        return await self._func(*args_to_pass, **kwargs_to_pass)
    def stop(self) -> None:
        """停止这个 effect,使其不再响应 Ref 变化。"""
        self._is_active = False
        # 在这里,如果 Ref 内部存储的是 EffectWrapper 实例,
        # 则可以遍历 Ref 的 _subscribers 并移除 self。
        # 但这需要 Ref 暴露一个 API 或 EffectWrapper 持有 Ref 的引用,
        # 为了简化,我们只设置 _is_active。
        print(f"Effect '{self._func.__name__}' stopped.")
    
    @property
    def name(self) -> str:
        return self._func.__name__ + ("_async" if self._is_async else "_sync")

# --- 2. 装饰器 factory,返回一个 EffectWrapper 实例 ---
def effect(func: Callable) -> EffectWrapper:
    """
    一个通用的装饰器,返回一个 EffectWrapper 实例。
    """
    is_async = asyncio.iscoroutinefunction(func)
    return EffectWrapper(func, is_async)
