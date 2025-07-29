"""集成测试"""
import unittest
import asyncio
import time
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref import Ref, effect


class TestIntegration(unittest.TestCase):
    """集成测试类"""

    def test_complex_scenario(self) -> None:
        """测试复杂场景"""
        # 创建多个相关的 refs
        user_name = Ref("Alice")
        user_age = Ref(25)
        is_adult = Ref(True)
        
        # 记录各种变化
        greetings: list[str] = []
        age_changes: list[int] = []
        
        @effect
        def greeting_effect() -> None:
            greetings.append(f"Hello, {user_name.value}!")
        
        @effect
        def age_check_effect() -> None:
            is_adult.value = user_age.value >= 18
            age_changes.append(user_age.value)
        
        # 初始调用
        greeting_effect()
        age_check_effect()
        
        self.assertEqual(len(greetings), 1)
        self.assertEqual(greetings[0], "Hello, Alice!")
        self.assertEqual(len(age_changes), 1)
        self.assertEqual(is_adult.value, True)
        
        # 修改名字
        user_name.value = "Bob"
        self.assertEqual(len(greetings), 2)
        self.assertEqual(greetings[1], "Hello, Bob!")
        
        # 修改年龄
        user_age.value = 16
        self.assertEqual(len(age_changes), 2)
        self.assertEqual(is_adult.value, False)

    def test_performance(self) -> None:
        """简单性能测试"""
        ref = Ref(0)
        call_count = 0
        
        @effect
        def counter_effect() -> None:
            nonlocal call_count
            call_count += 1
            _ = ref.value
        
        # 初始调用
        counter_effect()
        self.assertEqual(call_count, 1)
        
        # 大量更新
        start_time = time.time()
        
        for i in range(1, 1001):  # 从 1 开始，避免重复设置相同值
            ref.value = i
        
        end_time = time.time()
        
        # 验证所有更新都触发了效果
        self.assertEqual(call_count, 1001)  # 初始 + 1000 次更新
        
        # 性能应该是合理的（少于1秒）
        self.assertLess(end_time - start_time, 1.0)

    def test_dependency_tracking(self) -> None:
        """测试依赖跟踪的正确性"""
        ref_a = Ref(1)
        ref_b = Ref(2)
        ref_c = Ref(3)
        
        a_calls = 0
        b_calls = 0
        
        @effect
        def effect_a() -> None:
            nonlocal a_calls
            a_calls += 1
            _ = ref_a.value  # 只依赖 ref_a
        
        @effect
        def effect_b() -> None:
            nonlocal b_calls
            b_calls += 1
            _ = ref_b.value  # 只依赖 ref_b
        
        # 初始调用
        effect_a()
        effect_b()
        
        self.assertEqual(a_calls, 1)
        self.assertEqual(b_calls, 1)
        
        # 修改 ref_a，只有 effect_a 应该被触发
        ref_a.value = 10
        self.assertEqual(a_calls, 2)
        self.assertEqual(b_calls, 1)
        
        # 修改 ref_b，只有 effect_b 应该被触发
        ref_b.value = 20
        self.assertEqual(a_calls, 2)
        self.assertEqual(b_calls, 2)
        
        # 修改 ref_c，两个 effect 都不应该被触发
        ref_c.value = 30
        self.assertEqual(a_calls, 2)
        self.assertEqual(b_calls, 2)

    def test_circular_dependency_prevention(self) -> None:
        """测试循环依赖预防"""
        ref_a = Ref(1)
        ref_b = Ref(2)
        
        call_count = 0
        
        @effect
        def circular_effect() -> None:
            nonlocal call_count
            call_count += 1
            
            # 读取 ref_a
            a_val = ref_a.value
            
            # 条件性地修改 ref_b，但不应该造成无限循环
            if call_count <= 2:  # 限制递归深度
                ref_b.value = a_val * 2
        
        circular_effect()
        
        # 应该有限制的调用次数，不是无限循环
        self.assertLessEqual(call_count, 5)

    def test_multiple_effect_chains(self) -> None:
        """测试多个 effect 链"""
        source = Ref(1)
        derived1 = Ref(0)
        derived2 = Ref(0)
        final = Ref(0)
        
        @effect
        def derive1() -> None:
            derived1.value = source.value * 2
        
        @effect
        def derive2() -> None:
            derived2.value = source.value * 3
        
        @effect
        def compute_final() -> None:
            final.value = derived1.value + derived2.value
        
        # 初始计算
        derive1()
        derive2()
        compute_final()
        
        self.assertEqual(derived1.value, 2)  # 1 * 2
        self.assertEqual(derived2.value, 3)  # 1 * 3
        self.assertEqual(final.value, 5)     # 2 + 3
        
        # 修改源值
        source.value = 5
        
        self.assertEqual(derived1.value, 10)  # 5 * 2
        self.assertEqual(derived2.value, 15)  # 5 * 3
        self.assertEqual(final.value, 25)     # 10 + 15


class TestIntegrationAsync(unittest.IsolatedAsyncioTestCase):
    """异步集成测试"""

    async def test_mixed_sync_async(self) -> None:
        """测试同步和异步混合使用"""
        data = Ref("initial")
        sync_calls: list[str] = []
        async_calls: list[str] = []
        
        @effect
        def sync_effect() -> None:
            sync_calls.append(data.value)
        
        @effect
        async def async_effect() -> None:
            async_calls.append(data.value)
            await asyncio.sleep(0.01)
        
        # 初始调用
        sync_effect()
        await async_effect()
        
        self.assertEqual(len(sync_calls), 1)
        self.assertEqual(len(async_calls), 1)
        
        # 修改数据
        data.value = "changed"
        
        # 同步效果应该立即触发
        self.assertEqual(len(sync_calls), 2)
        self.assertEqual(sync_calls[1], "changed")
        
        # 等待异步效果
        await asyncio.sleep(0.1)
        self.assertEqual(len(async_calls), 2)
        self.assertEqual(async_calls[1], "changed")

    async def test_async_computation_chain(self) -> None:
        """测试异步计算链"""
        input_ref = Ref(5)
        step1_ref = Ref(0)
        step2_ref = Ref(0)
        final_ref = Ref(0)
        
        @effect
        async def step1() -> None:
            await asyncio.sleep(0.01)  # 模拟异步计算
            step1_ref.value = input_ref.value * 2
        
        @effect
        async def step2() -> None:
            await asyncio.sleep(0.01)  # 模拟异步计算
            step2_ref.value = step1_ref.value + 10
        
        @effect
        async def final_step() -> None:
            await asyncio.sleep(0.01)  # 模拟异步计算
            final_ref.value = step2_ref.value * 3
        
        # 执行计算链
        await step1()
        await step2()
        await final_step()
        
        self.assertEqual(step1_ref.value, 10)   # 5 * 2
        self.assertEqual(step2_ref.value, 20)   # 10 + 10
        self.assertEqual(final_ref.value, 60)   # 20 * 3
        
        # 修改输入，等待链式反应
        input_ref.value = 10
        await asyncio.sleep(0.2)  # 等待所有异步操作完成
        
        # 验证最终结果
        self.assertEqual(step1_ref.value, 20)   # 10 * 2
        self.assertEqual(step2_ref.value, 30)   # 20 + 10
        self.assertEqual(final_ref.value, 90)   # 30 * 3

    async def test_error_isolation(self) -> None:
        """测试错误隔离"""
        trigger = Ref(0)
        success_calls = 0
        
        @effect
        async def failing_effect() -> None:
            _ = trigger.value
            if trigger.value > 0:
                raise ValueError("Intentional test error")
        
        @effect
        def success_effect() -> None:
            nonlocal success_calls
            success_calls += 1
            _ = trigger.value
        
        # 初始调用
        await failing_effect()
        success_effect()
        
        self.assertEqual(success_calls, 1)
        
        # 触发错误，但其他 effect 应该继续工作
        trigger.value = 1
        await asyncio.sleep(0.1)  # 等待异步错误处理
        
        # 成功的 effect 应该仍然被调用
        self.assertEqual(success_calls, 2)


if __name__ == '__main__':
    unittest.main()
