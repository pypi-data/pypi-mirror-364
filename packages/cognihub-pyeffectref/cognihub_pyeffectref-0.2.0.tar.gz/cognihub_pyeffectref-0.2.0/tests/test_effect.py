"""测试 effect 装饰器的功能"""
import unittest
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref import Ref, effect
from cognihub_pyeffectref.effect import EffectWrapper


class TestEffect(unittest.TestCase):
    """Effect 装饰器的测试"""

    def test_effect_creation(self) -> None:
        """测试 effect 创建"""
        @effect
        def test_func() -> None:
            pass

        self.assertIsInstance(test_func, EffectWrapper)

    def test_sync_effect(self) -> None:
        """测试同步 effect"""
        counter = Ref(0)
        call_count = 0

        @effect
        def sync_effect() -> None:
            nonlocal call_count
            call_count += 1
            _ = counter.value

        sync_effect()
        self.assertEqual(call_count, 1)

        counter.value = 1
        self.assertEqual(call_count, 2)

    def test_effect_stop(self) -> None:
        """测试 effect 停止"""
        counter = Ref(0)
        call_count = 0

        @effect
        def stoppable_effect() -> None:
            nonlocal call_count
            call_count += 1
            _ = counter.value

        stoppable_effect()
        self.assertEqual(call_count, 1)

        counter.value = 1
        self.assertEqual(call_count, 2)

        # 停止 effect
        stoppable_effect.stop()
        
        # 修改值，但 effect 已停止，不应该触发
        counter.value = 2
        self.assertEqual(call_count, 2)

    def test_multiple_refs_in_effect(self) -> None:
        """测试 effect 中使用多个 ref"""
        ref1 = Ref(1)
        ref2 = Ref(2)
        call_count = 0

        @effect
        def multi_ref_effect() -> None:
            nonlocal call_count
            call_count += 1
            _ = ref1.value + ref2.value

        multi_ref_effect()
        self.assertEqual(call_count, 1)

        ref1.value = 10
        self.assertEqual(call_count, 2)

        ref2.value = 20
        self.assertEqual(call_count, 3)

    def test_nested_effects(self) -> None:
        """测试嵌套 effects"""
        ref = Ref(0)
        outer_calls = 0
        inner_calls = 0

        @effect
        def inner_effect() -> None:
            nonlocal inner_calls
            inner_calls += 1
            _ = ref.value

        @effect
        def outer_effect() -> None:
            nonlocal outer_calls
            outer_calls += 1
            _ = ref.value
            inner_effect()

        outer_effect()
        self.assertEqual(outer_calls, 1)
        self.assertEqual(inner_calls, 1)

        ref.value = 1
        self.assertEqual(outer_calls, 2)
        self.assertGreaterEqual(inner_calls, 2)  # 可能会被调用多次

    def test_effect_with_parameters(self) -> None:
        """测试带参数的 effect"""
        ref = Ref(0)
        results = []

        @effect
        def effect_with_params(multiplier: int) -> int:
            value = ref.value * multiplier
            results.append(value)
            return value

        # 初始调用
        result = effect_with_params(2)
        self.assertEqual(result, 0)
        self.assertEqual(results[-1], 0)

        # 修改 ref，应该重新执行
        ref.value = 5
        self.assertEqual(len(results), 2)
        self.assertEqual(results[-1], 10)  # 5 * 2

    def test_effect_name_property(self) -> None:
        """测试 effect 的 name 属性"""
        @effect
        def my_sync_effect() -> None:
            pass

        @effect
        async def my_async_effect() -> None:
            pass

        self.assertEqual(my_sync_effect.name, "my_sync_effect_sync")
        self.assertEqual(my_async_effect.name, "my_async_effect_async")

    def test_effect_inactive_warning(self) -> None:
        """测试停止的 effect 调用时的警告"""
        @effect
        def test_effect() -> None:
            pass

        test_effect.stop()
        
        # 调用已停止的 effect 应该返回 None 并可能有警告
        result = test_effect()
        self.assertIsNone(result)

    def test_effect_without_dependencies(self) -> None:
        """测试没有依赖的 effect"""
        call_count = 0

        @effect
        def independent_effect() -> None:
            nonlocal call_count
            call_count += 1

        independent_effect()
        self.assertEqual(call_count, 1)

        # 没有依赖，所以不会再次触发
        # 这个测试主要确保不会崩溃


class TestEffectAsync(unittest.IsolatedAsyncioTestCase):
    """Effect 异步测试"""

    async def test_async_effect(self) -> None:
        """测试异步 effect"""
        counter = Ref(0)
        call_count = 0

        @effect
        async def async_effect() -> None:
            nonlocal call_count
            call_count += 1
            _ = counter.value
            await asyncio.sleep(0.01)

        await async_effect()
        self.assertEqual(call_count, 1)

        counter.value = 1
        # 需要等待一下让异步回调执行
        await asyncio.sleep(0.1)
        self.assertEqual(call_count, 2)

    async def test_async_effect_with_return_value(self) -> None:
        """测试有返回值的异步 effect"""
        ref = Ref(5)

        @effect
        async def async_computation() -> int:
            await asyncio.sleep(0.01)
            return ref.value * 2

        result = await async_computation()
        self.assertEqual(result, 10)

        ref.value = 10
        await asyncio.sleep(0.1)  # 等待触发的异步执行

    async def test_async_effect_exception_handling(self) -> None:
        """测试异步 effect 异常处理"""
        ref = Ref(0)

        @effect
        async def failing_async_effect() -> None:
            _ = ref.value
            if ref.value > 0:
                raise ValueError("Test exception")
            await asyncio.sleep(0.01)

        # 初始调用不应该抛出异常
        await failing_async_effect()

        # 触发异常的调用应该被捕获
        ref.value = 1
        await asyncio.sleep(0.1)  # 等待异步执行

    async def test_mixed_sync_async_effects_interaction(self) -> None:
        """测试同步和异步 effect 的交互"""
        shared_ref = Ref(0)
        sync_calls = []
        async_calls = []

        @effect
        def sync_effect() -> None:
            sync_calls.append(shared_ref.value)

        @effect
        async def async_effect() -> None:
            async_calls.append(shared_ref.value)
            await asyncio.sleep(0.01)

        # 初始执行
        sync_effect()
        await async_effect()

        self.assertEqual(len(sync_calls), 1)
        self.assertEqual(len(async_calls), 1)

        # 修改值，两个 effect 都应该被触发
        shared_ref.value = 42
        await asyncio.sleep(0.1)  # 等待异步执行

        self.assertEqual(len(sync_calls), 2)
        self.assertEqual(sync_calls[-1], 42)
        self.assertEqual(len(async_calls), 2)
        self.assertEqual(async_calls[-1], 42)


if __name__ == '__main__':
    unittest.main()
