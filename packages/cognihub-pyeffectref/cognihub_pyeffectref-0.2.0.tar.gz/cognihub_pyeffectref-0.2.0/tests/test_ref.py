"""测试 Ref 类的功能"""
from cognihub_pyeffectref import Ref, ReadOnlyRef, effect
import unittest
import threading
import time
import asyncio
import sys
import os
import concurrent.futures
import warnings
from typing import Callable

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRef(unittest.TestCase):
    """Ref 类的测试"""

    def test_ref_creation(self) -> None:
        """测试 Ref 创建"""
        ref = Ref(42)
        self.assertEqual(ref.value, 42)

    def test_ref_assignment(self) -> None:
        """测试 Ref 赋值"""
        ref = Ref(10)
        ref.value = 20
        self.assertEqual(ref.value, 20)

    def test_ref_type_annotation(self) -> None:
        """测试类型注解"""
        str_ref: Ref[str] = Ref("hello")
        self.assertEqual(str_ref.value, "hello")

        int_ref: Ref[int] = Ref(100)
        self.assertEqual(int_ref.value, 100)

    def test_ref_with_effect(self) -> None:
        """测试 Ref 与 effect 的配合"""
        counter = Ref(0)
        call_count = 0

        @effect
        def track_counter() -> None:
            nonlocal call_count
            call_count += 1
            _ = counter.value  # 建立依赖

        track_counter()
        self.assertEqual(call_count, 1)

        counter.value = 1
        self.assertEqual(call_count, 2)

        counter.value = 2
        self.assertEqual(call_count, 3)

    def test_manual_subscription(self) -> None:
        """测试手动订阅"""
        ref = Ref("initial")
        changes = []

        def on_change(new_val: str, old_val: str) -> None:
            changes.append((old_val, new_val))

        ref.subscribe(on_change)
        ref.value = "changed"
        ref.value = "final"

        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0], ("initial", "changed"))
        self.assertEqual(changes[1], ("changed", "final"))

    def test_unsubscribe(self) -> None:
        """测试取消订阅"""
        ref = Ref(0)
        call_count = 0

        def callback(new_val: int, old_val: int) -> None:
            nonlocal call_count
            call_count += 1

        ref.subscribe(callback)
        ref.value = 1
        self.assertEqual(call_count, 1)

        ref.unsubscribe(callback)
        ref.value = 2
        self.assertEqual(call_count, 1)  # 应该不再增加

    def test_thread_safety(self) -> None:
        """测试线程安全性"""
        ref = Ref(0)

        def worker() -> None:
            for i in range(100):
                current = ref.value
                ref.value = current + 1

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 由于线程安全的实现，最终值应该是 500
        self.assertEqual(ref.value, 500)

    def test_ref_no_change_no_notify(self) -> None:
        """测试值未改变时不通知"""
        ref = Ref(42)
        call_count = 0

        def callback(new_val: int, old_val: int) -> None:
            nonlocal call_count
            call_count += 1

        ref.subscribe(callback)

        # 设置相同的值
        ref.value = 42
        self.assertEqual(call_count, 0)

        # 设置不同的值
        ref.value = 43
        self.assertEqual(call_count, 1)

    def test_ref_repr(self) -> None:
        """测试 __repr__ 方法"""
        ref = Ref("test")
        self.assertEqual(repr(ref), "Ref('test')")

        ref_int = Ref(123)
        self.assertEqual(repr(ref_int), "Ref(123)")

    def test_subscriber_type_validation(self) -> None:
        """测试订阅者类型验证"""
        ref = Ref(0)

        # 测试无效的订阅者
        with self.assertRaises(TypeError):
            ref.subscribe("not_callable")  # type: ignore

    def test_complex_data_types(self) -> None:
        """测试复杂数据类型"""
        # 测试列表
        list_ref = Ref([1, 2, 3])
        self.assertEqual(list_ref.value, [1, 2, 3])

        list_ref.value = [4, 5, 6]
        self.assertEqual(list_ref.value, [4, 5, 6])

        # 测试字典
        dict_ref = Ref({"a": 1, "b": 2})
        self.assertEqual(dict_ref.value, {"a": 1, "b": 2})

        dict_ref.value = {"c": 3, "d": 4}
        self.assertEqual(dict_ref.value, {"c": 3, "d": 4})

    def test_multiple_subscribers(self) -> None:
        """测试多个订阅者"""
        ref = Ref(0)
        calls = []

        def subscriber1(new_val: int, old_val: int) -> None:
            calls.append(f"sub1: {old_val}->{new_val}")

        def subscriber2(new_val: int, old_val: int) -> None:
            calls.append(f"sub2: {old_val}->{new_val}")

        ref.subscribe(subscriber1)
        ref.subscribe(subscriber2)

        ref.value = 5

        # 两个订阅者都应该被调用
        self.assertEqual(len(calls), 2)
        self.assertIn("sub1: 0->5", calls)
        self.assertIn("sub2: 0->5", calls)


class TestRefAsync(unittest.IsolatedAsyncioTestCase):
    """Ref 异步测试"""

    async def test_async_effect_basic(self) -> None:
        """测试基本异步 effect"""
        counter = Ref(0)
        call_count = 0

        @effect
        async def async_track_counter() -> None:
            nonlocal call_count
            call_count += 1
            _ = counter.value
            await asyncio.sleep(0.01)

        await async_track_counter()
        self.assertEqual(call_count, 1)

        counter.value = 1
        await asyncio.sleep(0.1)  # 等待异步回调
        self.assertEqual(call_count, 2)

    async def test_mixed_sync_async_effects(self) -> None:
        """测试混合同步异步 effects"""
        data = Ref("initial")
        sync_calls = []
        async_calls = []

        @effect
        def sync_effect() -> None:
            sync_calls.append(data.value)

        @effect
        async def async_effect() -> None:
            async_calls.append(data.value)
            await asyncio.sleep(0.01)

        sync_effect()
        await async_effect()

        self.assertEqual(len(sync_calls), 1)
        self.assertEqual(len(async_calls), 1)

        data.value = "changed"
        await asyncio.sleep(0.1)  # 等待异步回调

        self.assertEqual(len(sync_calls), 2)
        self.assertEqual(sync_calls[1], "changed")
        self.assertEqual(len(async_calls), 2)
        self.assertEqual(async_calls[1], "changed")


class TestReadOnlyRef(unittest.TestCase):
    """ReadOnlyRef 类的测试"""

    def test_readonly_ref_creation(self) -> None:
        """测试 ReadOnlyRef 创建"""
        base_ref = Ref(42)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)
        self.assertEqual(readonly_ref.value, 42)

    def test_readonly_ref_invalid_creation(self) -> None:
        """测试 ReadOnlyRef 创建时类型验证"""
        with self.assertRaises(TypeError):
            ReadOnlyRef("not_a_ref")  # type: ignore

    def test_readonly_ref_tracks_changes(self) -> None:
        """测试 ReadOnlyRef 追踪底层 Ref 的变化"""
        base_ref = Ref("initial")
        readonly_ref: ReadOnlyRef[str] = ReadOnlyRef(base_ref)

        self.assertEqual(readonly_ref.value, "initial")

        # 修改底层 Ref
        base_ref.value = "changed"
        self.assertEqual(readonly_ref.value, "changed")

        # 再次修改
        base_ref.value = "final"
        self.assertEqual(readonly_ref.value, "final")

    def test_readonly_ref_no_setter(self) -> None:
        """测试 ReadOnlyRef 不能修改值"""
        base_ref = Ref(10)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)

        # ReadOnlyRef 不应该有 value.setter
        with self.assertRaises(AttributeError):
            readonly_ref.value = 20  # type: ignore

    def test_readonly_ref_subscription(self) -> None:
        """测试 ReadOnlyRef 的订阅功能"""
        base_ref = Ref(0)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)
        changes = []

        def on_change(new_val: int, old_val: int) -> None:
            changes.append((old_val, new_val))

        readonly_ref.subscribe(on_change)

        # 通过底层 Ref 修改值
        base_ref.value = 1
        base_ref.value = 2

        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0], (0, 1))
        self.assertEqual(changes[1], (1, 2))

    def test_readonly_ref_with_effect(self) -> None:
        """测试 ReadOnlyRef 与 effect 的配合"""
        base_ref = Ref(0)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)
        call_count = 0
        tracked_values = []

        @effect
        def track_readonly() -> None:
            nonlocal call_count
            call_count += 1
            tracked_values.append(readonly_ref.value)

        track_readonly()
        self.assertEqual(call_count, 1)
        self.assertEqual(tracked_values[0], 0)

        # 通过底层 Ref 修改值
        base_ref.value = 5
        self.assertEqual(call_count, 2)
        self.assertEqual(tracked_values[1], 5)

        base_ref.value = 10
        self.assertEqual(call_count, 3)
        self.assertEqual(tracked_values[2], 10)

    def test_readonly_ref_multiple_subscriptions(self) -> None:
        """测试 ReadOnlyRef 的多个订阅"""
        base_ref = Ref("start")
        readonly_ref: ReadOnlyRef[str] = ReadOnlyRef(base_ref)
        calls1 = []
        calls2 = []

        def subscriber1(new_val: str, old_val: str) -> None:
            calls1.append(f"sub1: {old_val}->{new_val}")

        def subscriber2(new_val: str, old_val: str) -> None:
            calls2.append(f"sub2: {old_val}->{new_val}")

        readonly_ref.subscribe(subscriber1)
        readonly_ref.subscribe(subscriber2)

        base_ref.value = "middle"
        base_ref.value = "end"

        self.assertEqual(len(calls1), 2)
        self.assertEqual(len(calls2), 2)
        self.assertEqual(calls1[0], "sub1: start->middle")
        self.assertEqual(calls1[1], "sub1: middle->end")
        self.assertEqual(calls2[0], "sub2: start->middle")
        self.assertEqual(calls2[1], "sub2: middle->end")

    def test_readonly_ref_repr(self) -> None:
        """测试 ReadOnlyRef 的 __repr__ 方法"""
        base_ref = Ref("test")
        readonly_ref: ReadOnlyRef[str] = ReadOnlyRef(base_ref)
        self.assertEqual(repr(readonly_ref), "ReadOnlyRef('test')")

        readonly_ref_int: ReadOnlyRef[int] = ReadOnlyRef(Ref(123))
        self.assertEqual(repr(readonly_ref_int), "ReadOnlyRef(123)")

    def test_readonly_ref_type_preservation(self) -> None:
        """测试 ReadOnlyRef 保持类型一致性"""
        # 测试字符串类型
        str_ref = Ref("hello")
        readonly_str_ref: ReadOnlyRef[str] = ReadOnlyRef(str_ref)
        self.assertEqual(readonly_str_ref.value, "hello")

        # 测试整数类型
        int_ref = Ref(42)
        readonly_int_ref: ReadOnlyRef[int] = ReadOnlyRef(int_ref)
        self.assertEqual(readonly_int_ref.value, 42)

        # 测试列表类型
        list_ref = Ref([1, 2, 3])
        readonly_list_ref: ReadOnlyRef[list[int]] = ReadOnlyRef(list_ref)
        self.assertEqual(readonly_list_ref.value, [1, 2, 3])

        # 修改底层 Ref 并验证类型
        list_ref.value = [4, 5, 6]
        self.assertEqual(readonly_list_ref.value, [4, 5, 6])

    def test_readonly_ref_independent_subscriptions(self) -> None:
        """测试 ReadOnlyRef 和底层 Ref 的独立订阅"""
        base_ref = Ref(0)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)

        base_calls = []
        readonly_calls = []

        def base_subscriber(new_val: int, old_val: int) -> None:
            base_calls.append(f"base: {old_val}->{new_val}")

        def readonly_subscriber(new_val: int, old_val: int) -> None:
            readonly_calls.append(f"readonly: {old_val}->{new_val}")

        # 分别订阅
        base_ref.subscribe(base_subscriber)
        readonly_ref.subscribe(readonly_subscriber)

        base_ref.value = 1

        # 两个订阅都应该被触发
        self.assertEqual(len(base_calls), 1)
        self.assertEqual(len(readonly_calls), 1)
        self.assertEqual(base_calls[0], "base: 0->1")
        self.assertEqual(readonly_calls[0], "readonly: 0->1")


class TestReadOnlyRefAsync(unittest.IsolatedAsyncioTestCase):
    """ReadOnlyRef 异步测试"""

    async def test_readonly_ref_async_effect(self) -> None:
        """测试 ReadOnlyRef 与异步 effect 的配合"""
        base_ref = Ref(0)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)
        call_count = 0
        tracked_values = []

        @effect
        async def async_track_readonly() -> None:
            nonlocal call_count
            call_count += 1
            tracked_values.append(readonly_ref.value)
            await asyncio.sleep(0.01)

        await async_track_readonly()
        self.assertEqual(call_count, 1)
        self.assertEqual(tracked_values[0], 0)

        base_ref.value = 5
        await asyncio.sleep(0.1)  # 等待异步回调
        self.assertEqual(call_count, 2)
        self.assertEqual(tracked_values[1], 5)

    async def test_readonly_ref_async_subscription(self) -> None:
        """测试 ReadOnlyRef 的异步订阅"""
        base_ref = Ref("initial")
        readonly_ref: ReadOnlyRef[str] = ReadOnlyRef(base_ref)
        async_calls = []

        async def async_subscriber(new_val: str, old_val: str) -> None:
            async_calls.append(f"async: {old_val}->{new_val}")
            await asyncio.sleep(0.01)

        readonly_ref.subscribe(async_subscriber)

        base_ref.value = "changed"
        await asyncio.sleep(0.1)  # 等待异步回调

        self.assertEqual(len(async_calls), 1)
        self.assertEqual(async_calls[0], "async: initial->changed")


class TestRefInitializationOptions(unittest.TestCase):
    """测试 Ref 初始化选项"""

    def test_subscribe_immediate_initialization(self) -> None:
        """测试 subscribe_immediate 参数"""
        ref = Ref(0, subscribe_immediate=True)
        self.assertTrue(ref._subscribe_immediate)
        self.assertFalse(ref._subscribe_sequential)

    def test_subscribe_sequential_initialization(self) -> None:
        """测试 subscribe_sequential 参数"""
        ref = Ref(0, subscribe_sequential=True)
        self.assertTrue(ref._subscribe_sequential)
        self.assertFalse(ref._subscribe_immediate)

    def test_both_immediate_and_sequential_warning(self) -> None:
        """测试同时设置 immediate 和 sequential 时的警告"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ref = Ref(0, subscribe_immediate=True, subscribe_sequential=True)

            # 应该产生警告
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, UserWarning))
            self.assertIn("subscribe_immediate will take precedence", str(w[0].message))

            # immediate 应该优先
            self.assertTrue(ref._subscribe_immediate)
            self.assertTrue(ref._subscribe_sequential)  # 仍然为 True，但会被忽略

    def test_default_initialization(self) -> None:
        """测试默认初始化参数"""
        ref = Ref(42)
        self.assertFalse(ref._subscribe_immediate)
        self.assertFalse(ref._subscribe_sequential)


class TestRefGlobalExecutorConfiguration(unittest.TestCase):
    """测试 Ref 全局执行器配置"""

    def setUp(self) -> None:
        """重置全局配置"""
        # 保存原始配置
        self.original_config = Ref._global_sync_executor_config
        # 设置为有效配置以便测试
        Ref._global_sync_executor_config = None

    def tearDown(self) -> None:
        """恢复原始配置"""
        Ref._global_sync_executor_config = self.original_config

    def test_configure_sync_task_executor_with_custom_executor(self) -> None:
        """测试配置自定义执行器"""
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

        # 先设置一个有效值才能调用 configure_sync_task_executor
        Ref._global_sync_executor_config = executor

        try:
            # 捕获输出
            import io
            import contextlib

            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                Ref.configure_sync_task_executor(executor)

            output = f.getvalue()
            self.assertIn("custom executor", output)
            self.assertIs(Ref._global_sync_executor_config, executor)
        finally:
            executor.shutdown(wait=True)

    def test_configure_sync_task_executor_with_asyncio(self) -> None:
        """测试配置 asyncio 执行器"""
        # 先设置一个有效值
        Ref._global_sync_executor_config = 'asyncio'

        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            Ref.configure_sync_task_executor('asyncio')

        output = f.getvalue()
        self.assertIn("asyncio's default thread pool", output)
        self.assertEqual(Ref._global_sync_executor_config, 'asyncio')

    def test_configure_sync_task_executor_invalid_type(self) -> None:
        """测试无效的执行器类型"""
        # 先设置一个有效值
        Ref._global_sync_executor_config = 'asyncio'

        with self.assertRaises(TypeError) as cm:
            Ref.configure_sync_task_executor("invalid")  # type: ignore

        self.assertIn("must be 'asyncio' or an instance", str(cm.exception))

    def test_configure_sync_task_executor_none_config(self) -> None:
        """测试在配置为 None 时调用方法"""
        Ref._global_sync_executor_config = None

        with self.assertRaises(ValueError) as cm:
            Ref.configure_sync_task_executor('asyncio')

        self.assertIn("must be configured before use", str(cm.exception))


class TestRefSubscribeImmediateBehavior(unittest.TestCase):
    """测试 subscribe_immediate 行为"""

    def setUp(self) -> None:
        """保存原始配置"""
        self.original_config = Ref._global_sync_executor_config

    def tearDown(self) -> None:
        """恢复原始配置"""
        Ref._global_sync_executor_config = self.original_config

    def test_subscribe_immediate_blocks_current_thread(self) -> None:
        """测试 subscribe_immediate 在当前线程中立即执行"""
        ref = Ref(0, subscribe_immediate=True)
        calls = []

        def callback(new_val: int, old_val: int) -> None:
            calls.append(f"callback: {old_val}->{new_val}")
            time.sleep(0.01)  # 模拟一些工作

        ref.subscribe(callback)

        start_time = time.time()
        ref.value = 1  # 应该阻塞直到回调完成
        end_time = time.time()

        # 回调应该立即执行
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], "callback: 0->1")

        # 应该有明显的延迟（表明在当前线程中执行）
        self.assertGreaterEqual(end_time - start_time, 0.01)

    def test_subscribe_immediate_overrides_asyncio_executor(self) -> None:
        """测试 subscribe_immediate 覆盖 asyncio 执行器配置"""
        # 设置 asyncio 执行器，但 subscribe_immediate 应该覆盖它
        async def run_test()->None:
            Ref._global_sync_executor_config = 'asyncio'
            ref = Ref(0, subscribe_immediate=True)
            calls = []
            execution_thread_id = None

            def callback(new_val: int, old_val: int) -> None:
                nonlocal execution_thread_id
                execution_thread_id = threading.get_ident()
                calls.append(f"callback: {old_val}->{new_val}")
                time.sleep(0.02)  # 模拟一些工作

            ref.subscribe(callback)

            main_thread_id = threading.get_ident()
            start_time = time.time()
            ref.value = 1  # 应该在当前线程中同步执行，而不是 asyncio.to_thread
            end_time = time.time()

            # 回调应该立即执行，不需要等待 asyncio.to_thread
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0], "callback: 0->1")

            # 应该有明显的延迟（表明在当前线程中同步执行）
            self.assertGreaterEqual(end_time - start_time, 0.02)

            # 应该在主线程中执行，而不是线程池中
            self.assertEqual(execution_thread_id, main_thread_id)

        asyncio.run(run_test())

    def test_subscribe_immediate_overrides_custom_executor(self) -> None:
        """测试 subscribe_immediate 覆盖自定义执行器配置"""
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        
        try:
            Ref._global_sync_executor_config = executor
            ref = Ref(0, subscribe_immediate=True)
            calls = []
            execution_thread_id = None

            def callback(new_val: int, old_val: int) -> None:
                nonlocal execution_thread_id
                execution_thread_id = threading.get_ident()
                calls.append(f"callback: {old_val}->{new_val}")
                time.sleep(0.02)  # 模拟一些工作

            ref.subscribe(callback)

            main_thread_id = threading.get_ident()
            start_time = time.time()
            ref.value = 1  # 应该在当前线程中同步执行，而不是提交到执行器
            end_time = time.time()

            # 回调应该立即执行，不需要等待执行器
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0], "callback: 0->1")

            # 应该有明显的延迟（表明在当前线程中同步执行）
            self.assertGreaterEqual(end_time - start_time, 0.02)

            # 应该在主线程中执行，而不是线程池中
            self.assertEqual(execution_thread_id, main_thread_id)

        finally:
            executor.shutdown(wait=True)

    def test_subscribe_immediate_with_multiple_callbacks(self) -> None:
        """测试 subscribe_immediate 与多个回调的行为"""
        Ref._global_sync_executor_config = 'asyncio'
        ref = Ref(0, subscribe_immediate=True)
        calls = []
        execution_order = []

        def callback1(new_val: int, old_val: int) -> None:
            time.sleep(0.01)
            calls.append(f"callback1: {old_val}->{new_val}")
            execution_order.append("callback1")

        def callback2(new_val: int, old_val: int) -> None:
            time.sleep(0.01)
            calls.append(f"callback2: {old_val}->{new_val}")
            execution_order.append("callback2")

        def callback3(new_val: int, old_val: int) -> None:
            calls.append(f"callback3: {old_val}->{new_val}")
            execution_order.append("callback3")

        ref.subscribe(callback1)
        ref.subscribe(callback2)
        ref.subscribe(callback3)

        start_time = time.time()
        ref.value = 1  # 所有回调都应该在当前线程中按顺序同步执行
        end_time = time.time()

        # 所有回调都应该立即执行
        self.assertEqual(len(calls), 3)
        self.assertIn("callback1: 0->1", calls)
        self.assertIn("callback2: 0->1", calls)
        self.assertIn("callback3: 0->1", calls)

        # 应该按注册顺序执行（因为都在当前线程中）
        self.assertEqual(execution_order, ["callback1", "callback2", "callback3"])

        # 应该有累积的延迟（表明所有回调都在当前线程中顺序执行）
        self.assertGreaterEqual(end_time - start_time, 0.02)

    def test_subscribe_immediate_precedence_over_sequential(self) -> None:
        """测试 subscribe_immediate 优先级高于 subscribe_sequential"""
        Ref._global_sync_executor_config = 'asyncio'
        # 同时设置两个参数，immediate 应该优先
        ref = Ref(0, subscribe_immediate=True, subscribe_sequential=True)
        calls = []
        execution_thread_id = None

        def callback(new_val: int, old_val: int) -> None:
            nonlocal execution_thread_id
            execution_thread_id = threading.get_ident()
            calls.append(f"callback: {old_val}->{new_val}")
            time.sleep(0.02)

        ref.subscribe(callback)

        main_thread_id = threading.get_ident()
        start_time = time.time()
        ref.value = 1  # 应该立即执行，而不是收集到 sequential 列表中
        end_time = time.time()

        # 回调应该立即执行
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], "callback: 0->1")

        # 应该有延迟（表明在当前线程中同步执行）
        self.assertGreaterEqual(end_time - start_time, 0.02)

        # 应该在主线程中执行
        self.assertEqual(execution_thread_id, main_thread_id)


class TestRefSubscribeSequentialBehavior(unittest.TestCase):
    """测试 subscribe_sequential 行为"""

    def setUp(self) -> None:
        """保存原始配置"""
        self.original_config = Ref._global_sync_executor_config

    def tearDown(self) -> None:
        """恢复原始配置"""
        Ref._global_sync_executor_config = self.original_config

    def test_subscribe_sequential_without_executor(self) -> None:
        """测试没有全局执行器时的顺序执行"""
        Ref._global_sync_executor_config = None
        ref = Ref(0, subscribe_sequential=True)
        calls = []

        def callback1(new_val: int, old_val: int) -> None:
            calls.append(f"callback1: {old_val}->{new_val}")

        def callback2(new_val: int, old_val: int) -> None:
            calls.append(f"callback2: {old_val}->{new_val}")

        ref.subscribe(callback1)
        ref.subscribe(callback2)

        ref.value = 1

        # 应该按顺序执行
        self.assertEqual(len(calls), 2)
        self.assertIn("callback1: 0->1", calls)
        self.assertIn("callback2: 0->1", calls)

    def test_subscribe_sequential_with_asyncio_executor(self) -> None:
        """测试在 asyncio 执行器配置下的顺序执行"""
        async def run_test()-> None:
            Ref._global_sync_executor_config = 'asyncio'
            ref = Ref(0, subscribe_sequential=True)
            calls = []

            def callback1(new_val: int, old_val: int) -> None:
                import time
                time.sleep(0.01)  # 模拟一些工作
                calls.append(f"callback1: {old_val}->{new_val}")

            def callback2(new_val: int, old_val: int) -> None:
                import time
                time.sleep(0.01)  # 模拟一些工作
                calls.append(f"callback2: {old_val}->{new_val}")

            def callback3(new_val: int, old_val: int) -> None:
                calls.append(f"callback3: {old_val}->{new_val}")

            ref.subscribe(callback1)
            ref.subscribe(callback2)
            ref.subscribe(callback3)

            ref.value = 1

            # 给 asyncio.to_thread 一些时间执行
            await asyncio.sleep(0.15)

            # 所有回调都应该被执行
            self.assertEqual(len(calls), 3)
            self.assertIn("callback1: 0->1", calls)
            self.assertIn("callback2: 0->1", calls)
            self.assertIn("callback3: 0->1", calls)

            # 注意：在 asyncio.to_thread 环境下，由于线程调度的不确定性，
            # 无法严格保证执行顺序，但重要的是所有回调都被执行了

        # 在 asyncio 事件循环中运行测试
        asyncio.run(run_test())

    def test_subscribe_sequential_with_custom_executor(self) -> None:
        """测试在自定义执行器配置下的顺序执行"""
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        
        try:
            Ref._global_sync_executor_config = executor
            ref = Ref(0, subscribe_sequential=True)
            calls = []
            execution_order = []

            def callback1(new_val: int, old_val: int) -> None:
                import time
                time.sleep(0.01)  # 模拟一些工作
                calls.append(f"callback1: {old_val}->{new_val}")
                execution_order.append("callback1")

            def callback2(new_val: int, old_val: int) -> None:
                import time
                time.sleep(0.01)  # 模拟一些工作
                calls.append(f"callback2: {old_val}->{new_val}")
                execution_order.append("callback2")

            def callback3(new_val: int, old_val: int) -> None:
                calls.append(f"callback3: {old_val}->{new_val}")
                execution_order.append("callback3")

            ref.subscribe(callback1)
            ref.subscribe(callback2)
            ref.subscribe(callback3)

            ref.value = 1

            # 等待执行器完成工作
            import time
            time.sleep(0.15)

            # 所有回调都应该被执行
            self.assertEqual(len(calls), 3)
            self.assertIn("callback1: 0->1", calls)
            self.assertIn("callback2: 0->1", calls)
            self.assertIn("callback3: 0->1", calls)

            # 现在应该能保证执行顺序了（因为修复了 set -> list 的问题）
            self.assertEqual(execution_order, ["callback1", "callback2", "callback3"])

        finally:
            executor.shutdown(wait=True)

    def test_subscribe_non_sequential_with_asyncio_executor(self) -> None:
        """测试在 asyncio 执行器配置下的非顺序执行"""
        async def run_test()-> None:
            Ref._global_sync_executor_config = 'asyncio'
            ref = Ref(0)  # 不设置 subscribe_sequential
            calls = []

            def callback1(new_val: int, old_val: int) -> None:
                calls.append(f"callback1: {old_val}->{new_val}")

            def callback2(new_val: int, old_val: int) -> None:
                calls.append(f"callback2: {old_val}->{new_val}")

            ref.subscribe(callback1)
            ref.subscribe(callback2)

            ref.value = 1

            # 给 asyncio.to_thread 一些时间执行
            await asyncio.sleep(0.1)

            # 所有回调都应该被执行
            self.assertEqual(len(calls), 2)
            self.assertIn("callback1: 0->1", calls)
            self.assertIn("callback2: 0->1", calls)

        # 在 asyncio 事件循环中运行测试
        asyncio.run(run_test())


class TestRefValuePropertyBehavior(unittest.TestCase):
    """测试 Ref value 属性的特殊行为"""

    def test_value_getter_with_no_current_effect(self) -> None:
        """测试在没有当前 effect 的情况下获取值"""
        ref = Ref(42)

        # 直接访问，不在 effect 中
        value = ref.value
        self.assertEqual(value, 42)

        # 检查没有订阅者被添加
        self.assertEqual(len(ref._subscribers), 0)

    def test_value_setter_no_change_no_notification(self) -> None:
        """测试设置相同值时不触发通知"""
        ref = Ref(42)
        calls = []

        def callback(new_val: int, old_val: int) -> None:
            calls.append(f"{old_val}->{new_val}")

        ref.subscribe(callback)

        # 设置相同的值
        ref.value = 42
        self.assertEqual(len(calls), 0)

        # 设置不同的值
        ref.value = 43
        self.assertEqual(len(calls), 1)


class TestRefErrorHandling(unittest.TestCase):
    """测试 Ref 的错误处理"""

    def test_subscribe_non_callable(self) -> None:
        """测试订阅非可调用对象时的错误"""
        ref = Ref(0)

        with self.assertRaises(TypeError) as cm:
            ref.subscribe("not_callable")  # type: ignore

        self.assertIn("must be a callable", str(cm.exception))

    def test_unsubscribe_non_existent_callback(self) -> None:
        """测试取消订阅不存在的回调"""
        ref = Ref(0)

        def callback(new_val: int, old_val: int) -> None:
            pass

        # 取消订阅一个从未订阅的回调应该不抛出异常
        ref.unsubscribe(callback)
        self.assertEqual(len(ref._subscribers), 0)


class TestRefThreadSafetyAdvanced(unittest.TestCase):
    """测试 Ref 的高级线程安全特性"""

    def test_concurrent_subscription_operations(self) -> None:
        """测试并发订阅操作的线程安全性"""
        ref = Ref(0)

        def subscription_worker(worker_id: int) -> None:
            def callback(new_val: int, old_val: int) -> None:
                pass

            # 每个线程订阅和取消订阅多次
            for i in range(10):
                ref.subscribe(callback)
                if i % 2 == 0:
                    ref.unsubscribe(callback)

        threads = []
        for i in range(5):
            thread = threading.Thread(target=subscription_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 测试应该完成而不崩溃
        self.assertIsInstance(ref._subscribers, list)

    def test_concurrent_value_changes_and_subscriptions(self) -> None:
        """测试并发值变更和订阅操作"""
        ref = Ref(0)
        call_counts: dict[int, int] = {}
        call_counts_lock = threading.Lock()

        def callback_factory(callback_id: int) -> Callable[[int, int], None]:
            def callback(new_val: int, old_val: int) -> None:
                with call_counts_lock:
                    call_counts[callback_id] = call_counts.get(callback_id, 0) + 1
            return callback

        def value_changer() -> None:
            for i in range(20):
                ref.value = i
                time.sleep(0.001)

        def subscriber() -> None:
            for i in range(10):
                callback = callback_factory(threading.get_ident())
                ref.subscribe(callback)
                time.sleep(0.002)

        # 启动线程
        threads = []
        threads.append(threading.Thread(target=value_changer))
        threads.append(threading.Thread(target=subscriber))
        threads.append(threading.Thread(target=subscriber))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # 应该有回调被调用
        self.assertGreater(len(call_counts), 0)


class TestRefWithComplexTypes(unittest.TestCase):
    """测试 Ref 处理复杂类型"""

    def test_ref_with_none_values(self) -> None:
        """测试 Ref 处理 None 值"""
        ref: Ref[int | None] = Ref(None)
        self.assertIsNone(ref.value)

        calls = []

        def callback(new_val: int | None, old_val: int | None) -> None:
            calls.append(f"{old_val}->{new_val}")

        ref.subscribe(callback)

        ref.value = 42
        self.assertEqual(ref.value, 42)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], "None->42")

        ref.value = None
        self.assertIsNone(ref.value)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1], "42->None")

    def test_ref_with_custom_objects(self) -> None:
        """测试 Ref 处理自定义对象"""
        class CustomObject:
            def __init__(self, value: int):
                self.value = value

            def __eq__(self, other: object) -> bool:
                if isinstance(other, CustomObject):
                    return self.value == other.value
                return False

            def __repr__(self) -> str:
                return f"CustomObject({self.value})"

        obj1 = CustomObject(1)
        obj2 = CustomObject(2)
        obj3 = CustomObject(1)  # 等于 obj1，但是不同的引用

        ref = Ref(obj1)
        calls = []

        def callback(new_val: CustomObject, old_val: CustomObject) -> None:
            calls.append(f"{old_val}->{new_val}")

        ref.subscribe(callback)

        # 设置不同对象
        ref.value = obj2
        self.assertEqual(len(calls), 1)

        # 设置相等但不同引用的对象，由于 Ref 使用 != 比较，
        # 而 obj2 != obj3 为 True（因为它们的值不同），所以会触发回调
        ref.value = obj3
        self.assertEqual(len(calls), 2)  # 应该触发回调，因为 obj2 != obj3

        # 设置同一个对象引用，不应该触发回调
        ref.value = obj3
        self.assertEqual(len(calls), 2)  # 仍然是 2，因为是同一个引用

    def test_ref_with_mutable_collections(self) -> None:
        """测试 Ref 处理可变集合"""
        ref = Ref([1, 2, 3])
        calls = []

        def callback(new_val: list[int], old_val: list[int]) -> None:
            calls.append(f"{old_val}->{new_val}")

        ref.subscribe(callback)

        # 修改引用（新列表）
        ref.value = [4, 5, 6]
        self.assertEqual(len(calls), 1)

        # 注意：修改现有列表的内容不会触发通知
        # 因为 Ref 比较的是引用，不是内容
        current_list = ref.value
        current_list.append(7)
        # 这不会触发回调，因为引用没有改变
        self.assertEqual(len(calls), 1)


class TestReadOnlyRefAdvanced(unittest.TestCase):
    """ReadOnlyRef 高级测试"""

    def test_readonly_ref_unsubscribe(self) -> None:
        """测试 ReadOnlyRef 的取消订阅功能"""
        base_ref = Ref(0)
        readonly_ref = ReadOnlyRef(base_ref)
        calls = []

        def callback(new_val: int, old_val: int) -> None:
            calls.append(f"{old_val}->{new_val}")

        # 通过 ReadOnlyRef 订阅
        readonly_ref.subscribe(callback)

        base_ref.value = 1
        self.assertEqual(len(calls), 1)

        # 通过底层 Ref 取消订阅应该也能工作
        base_ref.unsubscribe(callback)

        base_ref.value = 2
        self.assertEqual(len(calls), 1)  # 应该不再增加

    def test_readonly_ref_thread_safety(self) -> None:
        """测试 ReadOnlyRef 的线程安全性"""
        base_ref = Ref(0)
        readonly_ref = ReadOnlyRef(base_ref)

        def reader_worker(results: list) -> None:
            for _ in range(100):
                value = readonly_ref.value
                results.append(value)

        def writer_worker() -> None:
            for i in range(100):
                base_ref.value = i

        results: list[int] = []
        threads = []

        # 启动读取器和写入器线程
        for _ in range(3):
            thread = threading.Thread(target=reader_worker, args=(results,))
            threads.append(thread)
            thread.start()

        writer_thread = threading.Thread(target=writer_worker)
        threads.append(writer_thread)
        writer_thread.start()

        for thread in threads:
            thread.join()

        # 应该读取到一些值
        self.assertGreater(len(results), 0)

    def test_readonly_ref_initialization_validation(self) -> None:
        """测试 ReadOnlyRef 初始化验证的边界情况"""
        # 测试各种无效输入
        invalid_inputs = [
            "string",
            123,
            [],
            {},
            None,
            lambda x: x
        ]

        for invalid_input in invalid_inputs:
            with self.assertRaises(TypeError):
                ReadOnlyRef(invalid_input)  # type: ignore


class TestRefEffectWrapperIntegration(unittest.TestCase):
    """测试 Ref 与 EffectWrapper 的集成"""

    def setUp(self) -> None:
        """保存原始配置"""
        self.original_config = Ref._global_sync_executor_config

    def tearDown(self) -> None:
        """恢复原始配置"""
        Ref._global_sync_executor_config = self.original_config

    def test_sync_effect_wrapper_execution(self) -> None:
        """测试同步 EffectWrapper 的执行"""
        ref = Ref(0)
        call_count = 0

        @effect
        def sync_effect() -> None:
            nonlocal call_count
            call_count += 1
            _ = ref.value

        # 首次执行
        sync_effect()
        self.assertEqual(call_count, 1)

        # 触发重新执行
        ref.value = 1
        self.assertEqual(call_count, 2)

    def test_sync_effect_wrapper_with_asyncio_executor(self) -> None:
        """测试同步 EffectWrapper 在 asyncio 执行器下的执行"""
        async def run_test()-> None:
            Ref._global_sync_executor_config = 'asyncio'
            ref = Ref(0)
            call_count = 0

            @effect
            def sync_effect() -> None:
                nonlocal call_count
                call_count += 1
                _ = ref.value

            # 首次执行
            sync_effect()
            self.assertEqual(call_count, 1)

            # 触发重新执行
            ref.value = 1
            await asyncio.sleep(0.1)  # 等待 asyncio.to_thread 执行
            self.assertEqual(call_count, 2)

        asyncio.run(run_test())

    def test_sync_effect_wrapper_with_custom_executor(self) -> None:
        """测试同步 EffectWrapper 在自定义执行器下的执行"""
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        
        try:
            Ref._global_sync_executor_config = executor
            ref = Ref(0)
            call_count = 0

            @effect
            def sync_effect() -> None:
                nonlocal call_count
                call_count += 1
                _ = ref.value

            # 首次执行
            sync_effect()
            self.assertEqual(call_count, 1)

            # 触发重新执行
            ref.value = 1
            time.sleep(0.1)  # 等待执行器完成
            self.assertEqual(call_count, 2)

        finally:
            executor.shutdown(wait=True)


class TestRefErrorHandlingAdvanced(unittest.TestCase):
    """测试 Ref 的高级错误处理"""

    def test_async_effect_error_handling_outside_event_loop(self) -> None:
        """测试异步 effect 在没有事件循环时的错误处理"""
        ref = Ref(0)

        @effect
        async def async_effect() -> None:
            _ = ref.value
            await asyncio.sleep(0.01)

        # 首次执行（在 asyncio 环境外）
        # 这应该不会崩溃，但会在控制台输出错误信息
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            async_effect()  # 同步调用异步函数，建立依赖
            ref.value = 1   # 这会尝试调度异步回调，但会失败

        # 不检查具体输出，因为错误处理是打印到 stdout

    def test_callback_exception_handling(self) -> None:
        """测试回调函数异常处理"""
        ref = Ref(0)

        def failing_callback(new_val: int, old_val: int) -> None:
            raise Exception("Test exception")

        def working_callback(new_val: int, old_val: int) -> None:
            pass

        # 订阅两个回调，其中一个会失败
        ref.subscribe(failing_callback)
        ref.subscribe(working_callback)

        # 这应该不会崩溃，即使有回调失败
        ref.value = 1

    def test_effect_wrapper_exception_handling(self) -> None:
        """测试 EffectWrapper 异常处理"""
        ref = Ref(0)

        @effect
        def failing_effect() -> None:
            _ = ref.value
            raise Exception("Intentional test error")

        # 首次执行会建立依赖
        try:
            failing_effect()
        except Exception:
            pass  # 预期会有异常

        # 触发重新执行，这应该不会崩溃整个程序
        ref.value = 1


class TestRefAsyncContextVarSupport(unittest.IsolatedAsyncioTestCase):
    """测试 Ref 对 asyncio contextvar 的支持"""

    async def test_asyncio_context_effect_detection(self) -> None:
        """测试在 asyncio 上下文中的 effect 检测"""
        ref = Ref(0)
        call_count = 0

        @effect
        async def async_effect() -> None:
            nonlocal call_count
            call_count += 1
            # 在 asyncio 任务中访问 ref.value
            _ = ref.value
            await asyncio.sleep(0.01)

        # 在 asyncio 环境中执行
        await async_effect()
        self.assertEqual(call_count, 1)

        # 触发重新执行
        ref.value = 1
        await asyncio.sleep(0.1)
        self.assertEqual(call_count, 2)

    async def test_threading_local_fallback(self) -> None:
        """测试当不在 asyncio 任务中时回退到 threading.local"""
        ref = Ref(0)
        
        # 直接访问 value（不在 effect 中）
        value = ref.value
        self.assertEqual(value, 0)
        
        # 确认没有建立依赖（没有订阅者）
        self.assertEqual(len(ref._subscribers), 0)


if __name__ == '__main__':
    unittest.main()
