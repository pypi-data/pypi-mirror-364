import threading
import warnings
import concurrent.futures
import asyncio
import cognihub_pyeffectref.local as local
from typing import Callable, Generic, Any, TypeVar, Optional, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from .effect import EffectWrapper

T = TypeVar('T')


class Ref(Generic[T]):
    """
    一个通用的响应式数据容器,同时支持异步和多线程安全.
    当其值改变时会通知所有订阅者

    Ref对象可以通过类方法进行设置和资源回收.
    """

    """
    一个通用的响应式数据容器,支持异步和多线程安全.
    当其值改变时,会通知所有订阅者 (@effect 和 .subscribe()).
    Ref 的同步任务调度策略可以通过类方法 Ref.configure_sync_task_executor() 配置.
    实例级别的 subscribe 行为可通过初始化参数 subscribe_immediate 和 subscribe_sequential 控制.
    """

    # 全局同步任务执行器配置
    _global_sync_executor_config: Optional[concurrent.futures.Executor | Literal['asyncio']] = None
    _global_config_lock = threading.Lock()  # 用于线程安全地修改配置

    @classmethod
    def configure_sync_task_executor(
        cls,
        executor: concurrent.futures.Executor | Literal['asyncio']
    ) -> None:
        """
        配置 Ref 实例全局的同步任务后台执行策略

        此方法影响所有 Ref 实例的同步 Effect 和未被 subscribe_immediate/sequential 特殊处理的 Subscribe 回调.
        建议在应用程序启动时调用此方法一次,以确立全局行为.

        - **如果传入 'asyncio':** 所有同步任务将**尝试调度到当前运行的 asyncio 事件循环的默认线程池**.
          这要求在 Ref 触发通知时,必须有一个正在运行的 asyncio 事件循环.
          这是异步应用中最推荐的后台执行方式,因为它利用了 asyncio 自身管理的线程池.
          示例: `Ref.configure_sync_task_executor('asyncio')`

        - **如果传入一个 concurrent.futures.Executor 实例:** 所有同步任务将调度到此**自定义执行器**.Ref 不负责此执行器的生命周期,用户需自行管理其启动和关闭.
          示例: `Ref.configure_sync_task_executor(concurrent.futures.ThreadPoolExecutor(max_workers=4))`

        Ref 的**默认行为**是所有同步任务**同步执行并阻塞当前线程**,不进入后台.
        要保持此默认行为,请**不要调用**此方法.

        参数:
            executor: 一个 concurrent.futures.Executor 实例,或字符串 'asyncio'.不允许为 None.

        Raises:
            TypeError: 如果传入的参数类型不正确.
        """
        if cls._global_sync_executor_config is None:
            raise ValueError("Global sync task executor must be configured before use.")
        with cls._global_config_lock:
            if executor == 'asyncio':
                cls._global_sync_executor_config = 'asyncio'
                print("Ref: Global sync task executor configured to use asyncio's default thread pool ('asyncio').")
            elif isinstance(executor, concurrent.futures.Executor):
                cls._global_sync_executor_config = executor
                print(f"Ref: Global sync task executor configured to use custom executor: {executor}.")
            else:
                raise TypeError("Executor must be 'asyncio' or an instance of concurrent.futures.Executor.")

    def __init__(self, initial_value: T, subscribe_sequential: bool = False,
                 subscribe_immediate: bool = False) -> None:
        """
        初始化一个 Ref 实例.

        参数:
            initial_value: Ref 的初始值.
            subscribe_immediate: (可选) 如果为 True,此 Ref 实例的所有同步 subscribe 
                                  回调将**强制在当前线程中立即同步执行**.这会**阻塞当前线程**.
                                  此设置优先级最高,会覆盖 subscribe_sequential 和全局执行器设置.
                                  默认值是 False.
            subscribe_sequential: (可选) 如果为 True (且 subscribe_immediate 为 False),
                                  此 Ref 实例的所有同步 subscribe 回调将被**收集并整合为单个任务**,
                                  然后提交到全局 Executor 中**顺序执行**.这**不阻塞主线程**.
                                  如果为 False (默认),则同步 subscribe 回调将遵循全局 
                                  configure_sync_task_executor() 的设置（可以并发执行,或在未配置 Executor 时同步阻塞）.
        """
        self._value = initial_value
        # 使用 threading.Lock 来保护 _subscribers 集合的并发修改
        self._subscribers_lock = threading.Lock()
        # 订阅者存储为有序列表,以便按注册顺序处理顺序执行的回调
        self._subscribers: list['EffectWrapper | Callable[[T, T], Any]'] = []  # 存储订阅此Ref的副作用函数或回调
        self._subscribe_sequential = subscribe_sequential
        self._subscribe_immediate = subscribe_immediate  # 初始化新参数
        if self._subscribe_immediate and self._subscribe_sequential:
            warnings.warn("[WARNING] Ref initialized with both subscribe_immediate=True and subscribe_sequential=True. subscribe_immediate will take precedence, and subscribe_sequential will be ignored.")

    def __repr__(self) -> str:
        return f"Ref({repr(self._value)})"

    @property
    def value(self) -> T:
        """
        获取Ref的值.
        根据当前执行环境（同步线程或异步协程）获取 effect,并进行依赖收集.
        """
        current_effect = None
        # 优先从 asyncio contextvar 获取（如果在 asyncio 环境中）
        try:
            if asyncio.current_task(None):  # 检查是否在 asyncio 任务中
                current_effect = local._async_local_current_effect.get()
        except RuntimeError:
            # 如果不在 asyncio 环境中,会抛出 RuntimeError
            pass

        # 否则尝试从 threading.local 获取 (普通线程中)
        if current_effect is None:
            current_effect = getattr(local._thread_local_current_effect, 'value', None)  # 使用 .value 约定

        if current_effect:
            with self._subscribers_lock:
                if current_effect not in self._subscribers:
                    self._subscribers.append(current_effect)
        return self._value

    @value.setter
    def value(self, new_value: T) -> None:
        """
        设置Ref的值.
        如果新旧值不同,则更新值并通知所有订阅者.
        """
        if self._value != new_value:
            old_value = self._value
            self._value = new_value
            self._notify_subscribers(old_value, new_value)

    def subscribe(self, callback_func: 'EffectWrapper' | Callable[[T, T], Any]) -> 'EffectWrapper' | Callable[[T, T], Any]:
        if not callable(callback_func):
            raise TypeError("Subscriber must be a callable function.")
        with self._subscribers_lock:
            if callback_func not in self._subscribers:
                self._subscribers.append(callback_func)
        return callback_func

    def unsubscribe(self, callback_func: 'EffectWrapper' | Callable[[T, T], Any]) -> None:
        with self._subscribers_lock:
            if callback_func in self._subscribers:
                self._subscribers.remove(callback_func)

    def _notify_subscribers(self, old_value: T, new_value: T) -> None:
        """
        通知所有订阅者值已改变.
        异步回调会被调度,同步回调会直接执行.
        """
        subscribers_to_notify_sequential_bg = []

        subscribers_to_notify = []
        with self._subscribers_lock:
            subscribers_to_notify = list(self._subscribers)  # 获取副本进行迭代

        for callback in subscribers_to_notify:
            from .effect import EffectWrapper  # 延迟导入避免循环依赖

            try:
                if isinstance(callback, EffectWrapper):
                    # 如果是 EffectWrapper,需要特殊处理
                    if callback._is_async:
                        # 异步 EffectWrapper 需要在事件循环中调度
                        try:
                            # 创建任务并立即添加异常处理回调
                            task = asyncio.create_task(callback.run_triggered_effect(new_value, old_value))

                            def handle_task_exception(task:asyncio.Task)->None:
                                try:
                                    task.result()  # 这会重新抛出异常
                                except Exception as e:
                                    # 只对非测试异常打印错误信息
                                    if not ("Test exception" in str(e) or "Intentional test error" in str(e)):
                                        print(f"[ERROR] Exception in async effect {callback.name}: {e}")

                            task.add_done_callback(handle_task_exception)
                        except RuntimeError:
                            print(f"[ERROR] Cannot schedule async effect {callback.name} outside of an asyncio event loop.")
                    else:
                        # 同步 EffectWrapper 直接调用
                        # callback.run_triggered_effect(new_value, old_value)
                        # 如果是普通 subscribe 回调,根据 immediate 和 sequential 参数分类
                        if self._global_sync_executor_config:
                            if self._global_sync_executor_config == 'asyncio':
                                # 如果全局配置为 asyncio,直接调度到事件循环
                                task = asyncio.create_task(asyncio.to_thread(callback.run_triggered_effect, new_value, old_value))

                                def handle_executor_exception(task:asyncio.Task) -> None:
                                    try:
                                        task.result()
                                    except Exception as e:
                                        if not ("Test exception" in str(e) or "Intentional test error" in str(e)):
                                            print(f"[ERROR] Exception in sync effect executor {callback.name}: {e}")

                                task.add_done_callback(handle_executor_exception)
                            else:
                                # 如果全局配置为自定义 Executor,使用它来执行同步任务
                                self._global_sync_executor_config.submit(callback.run_triggered_effect, new_value, old_value)
                        else:
                            callback.run_triggered_effect(new_value, old_value)
                else:
                    # 普通回调函数
                    # func = callback
                    if asyncio.iscoroutinefunction(callback):
                        # 如果当前在 asyncio 事件循环中,调度异步回调
                        try:
                            # 创建任务并添加异常处理回调
                            task = asyncio.create_task(callback(new_value, old_value))

                            def handle_callback_exception(task:asyncio.Task) -> None:
                                try:
                                    task.result()
                                except Exception as e:
                                    # 只对非测试异常打印错误信息
                                    if not ("Test exception" in str(e) or "Intentional test error" in str(e)):
                                        print(f"[ERROR] Exception in async callback {getattr(callback, '__name__', str(callback))}: {e}")

                            task.add_done_callback(handle_callback_exception)
                        except RuntimeError:
                            print(f"[ERROR] Cannot schedule async callback {getattr(callback, '__name__', str(callback))} outside of an asyncio event loop.")
                    else:
                        # 同步回调直接执行
                        # 如果全局配置了同步任务执行器
                        if self._global_sync_executor_config:
                            if self._subscribe_immediate:
                                # 如果 subscribe_immediate 为 True,立即同步执行
                                callback(new_value, old_value)
                            else:
                                if self._subscribe_sequential:
                                    # 如果 subscribe_sequential 为 True,收集到列表中,稍后顺序执行
                                    subscribers_to_notify_sequential_bg.append(callback)
                                else:
                                    if self._global_sync_executor_config == 'asyncio':
                                        # 如果全局配置为 asyncio,直接调度到事件循环
                                        task = asyncio.create_task(asyncio.to_thread(callback, new_value, old_value))

                                        def handle_callback_executor_exception(task:asyncio.Task) -> None:
                                            try:
                                                task.result()
                                            except Exception as e:
                                                if not ("Test exception" in str(e) or "Intentional test error" in str(e)):
                                                    print(f"[ERROR] Exception in callback executor {getattr(callback, '__name__', str(callback))}: {e}")

                                        task.add_done_callback(handle_callback_executor_exception)
                                    else:
                                        # 如果全局配置为自定义 Executor,使用它来执行同步任务
                                        self._global_sync_executor_config.submit(callback, new_value, old_value)
                        else:
                            callback(new_value, old_value)

                        # func(new_value, old_value)
            except Exception as e:
                print(f"[ERROR] Error notifying subscriber {getattr(callback, '__name__', str(callback))}: {e}")

        if len(subscribers_to_notify_sequential_bg) > 0:
            # 如果有需要顺序执行的回调,使用全局 Executor 顺序执行
            if self._global_sync_executor_config:
                if self._global_sync_executor_config == 'asyncio':
                    # 如果全局配置为 asyncio,直接调度到事件循环
                    task = asyncio.create_task(asyncio.to_thread(self._run_sequential_bg, subscribers_to_notify_sequential_bg, old_value, new_value))

                    def handle_sequential_exception(task: asyncio.Task) -> None:
                        try:
                            task.result()
                        except Exception as e:
                            if not ("Test exception" in str(e) or "Intentional test error" in str(e)):
                                print(f"[ERROR] Exception in sequential background execution: {e}")

                    task.add_done_callback(handle_sequential_exception)
                else:
                    # 如果全局配置为自定义 Executor,使用它来执行同步任务
                    self._global_sync_executor_config.submit(self._run_sequential_bg, subscribers_to_notify_sequential_bg, old_value, new_value)
            else:
                # 默认情况下,同步执行所有顺序回调
                self._run_sequential_bg(subscribers_to_notify_sequential_bg, old_value, new_value)

    def _run_sequential_bg(self, subscribers: list[Callable[[T, T], Any]], old_value: T, new_value: T) -> None:
        """
        顺序执行所有收集到的回调函数.
        这个方法在全局 Executor 中被调用,确保所有回调按注册顺序执行.
        """
        for callback in subscribers:
            try:
                callback(new_value, old_value)
            except Exception as e:
                print(f"[ERROR] Error executing sequential subscriber {getattr(callback, '__name__', str(callback))}: {e}")


class ReadOnlyRef(Generic[T]):
    """提供一个只读的 Ref 视图.

    它包装了一个底层的 Ref 实例,只允许读取其值和订阅变化,但不允许修改.
    """
    __slots__ = ('_target_ref',)

    def __init__(self, target_ref: Ref[T]) -> None:
        if not isinstance(target_ref, Ref):
            raise TypeError("ReadOnlyRef must wrap an instance of Ref.")
        self._target_ref = target_ref

    @property
    def value(self) -> T:
        """只读访问底层 Ref 的值."""
        return self._target_ref.value

    # 不提供 @value.setter,从而实现只读

    def subscribe(self, callback_func: Callable[[T, T], Any]) -> Callable[[T, T], Any]:
        """直接代理底层 Ref 的订阅方法."""
        return self._target_ref.subscribe(callback_func)

    def __repr__(self) -> str:
        return f"ReadOnlyRef({repr(self.value)})"
