"""测试 ReactiveDict 类的功能"""
import unittest
import json
import asyncio
import sys
import os
from typing import Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref import Ref, ReactiveDict, effect
class TestReactiveDict(unittest.TestCase):
    """ReactiveDict 类的基本测试"""

    def test_reactive_dict_creation(self) -> None:
        """测试 ReactiveDict 创建"""
        data = {"name": "Alice", "age": 30}
        rd: ReactiveDict = ReactiveDict(data)
        
        self.assertEqual(rd.name, "Alice")
        self.assertEqual(rd.age, 30)
        self.assertEqual(len(rd), 2)

    def test_dict_style_access(self) -> None:
        """测试字典风格访问"""
        data = {"key1": "value1", "key2": 42}
        rd: ReactiveDict = ReactiveDict(data)
        
        # 获取值
        self.assertEqual(rd["key1"], "value1")
        self.assertEqual(rd["key2"], 42)
        
        # 设置值
        rd["key1"] = "new_value"
        rd["key3"] = "added_value"
        
        self.assertEqual(rd["key1"], "new_value")
        self.assertEqual(rd["key3"], "added_value")
        self.assertEqual(len(rd), 3)

    def test_dot_notation_access(self) -> None:
        """测试字典风格访问（原点语法访问已移除）"""
        data = {"username": "bob", "score": 100}
        rd: ReactiveDict = ReactiveDict(data)
        
        # 获取值
        self.assertEqual(rd["username"], "bob")
        self.assertEqual(rd["score"], 100)
        
        # 设置值
        rd["username"] = "charlie"
        rd["level"] = 5
        
        self.assertEqual(rd["username"], "charlie")
        self.assertEqual(rd["level"], 5)

    def test_nested_dict_support(self) -> None:
        """测试嵌套字典支持"""
        data = {
            "user": {
                "info": {
                    "name": "Alice",
                    "age": 25
                },
                "preferences": {
                    "theme": "dark"
                }
            },
            "settings": {
                "debug": True
            }
        }
        rd: ReactiveDict = ReactiveDict(data)
        
        # 访问嵌套值 - 使用字典风格访问
        user_dict = rd["user"]
        self.assertIsInstance(user_dict, ReactiveDict)
        
        info_dict = user_dict["info"]
        self.assertIsInstance(info_dict, ReactiveDict)
        self.assertEqual(info_dict["name"], "Alice")
        self.assertEqual(info_dict["age"], 25)
        
        preferences_dict = user_dict["preferences"]
        self.assertIsInstance(preferences_dict, ReactiveDict)
        self.assertEqual(preferences_dict["theme"], "dark")
        
        settings_dict = rd["settings"]
        self.assertIsInstance(settings_dict, ReactiveDict)
        self.assertEqual(settings_dict["debug"], True)
        
        # 修改嵌套值
        user_dict["info"]["name"] = "Bob"
        user_dict["preferences"]["theme"] = "light"
        
        self.assertEqual(user_dict["info"]["name"], "Bob")
        self.assertEqual(user_dict["preferences"]["theme"], "light")

    def test_to_dict_conversion(self) -> None:
        """测试转换为普通字典"""
        data = {
            "simple": "value",
            "nested": {
                "inner": "data",
                "number": 42
            }
        }
        rd: ReactiveDict = ReactiveDict(data)
        
        # 修改一些值
        rd["simple"] = "modified"
        nested_dict = rd["nested"]
        nested_dict["inner"] = "changed"
        
        result = rd.to_dict()
        expected = {
            "simple": "modified",
            "nested": {
                "inner": "changed",
                "number": 42
            }
        }
        
        self.assertEqual(result, expected)
        self.assertIsInstance(result, dict)
        self.assertNotIsInstance(result["nested"], ReactiveDict)

    def test_delete_operation(self) -> None:
        """测试删除操作"""
        data = {"a": 1, "b": 2, "c": 3}
        rd: ReactiveDict = ReactiveDict(data)
        
        self.assertEqual(len(rd), 3)
        
        del rd["b"]
        self.assertEqual(len(rd), 2)
        self.assertNotIn("b", rd)
        
        # ReactiveDict 不再支持点符号访问，删除操作仅支持括号符号
        
        with self.assertRaises(KeyError):
            _ = rd["b"]
        
        with self.assertRaises(KeyError):
            del rd["nonexistent"]

    def test_iteration(self) -> None:
        """测试迭代功能"""
        data = {"x": 10, "y": 20, "z": 30}
        rd: ReactiveDict = ReactiveDict(data)
        
        keys = list(rd)
        self.assertEqual(set(keys), {"x", "y", "z"})
        
        # 测试items迭代
        items = {key: rd[key] for key in rd}
        self.assertEqual(items, data)

    def test_get_raw_ref(self) -> None:
        """测试获取底层 Ref 实例"""
        data = {
            "user": {
                "profile": {
                    "name": "Alice"
                }
            },
            "count": 5
        }
        rd: ReactiveDict = ReactiveDict(data)
        
        # 获取简单路径的 Ref
        count_ref = rd.get_raw_ref("count")
        self.assertIsInstance(count_ref, Ref)
        self.assertEqual(count_ref.value, 5)
        
        # 获取嵌套路径的 Ref
        name_ref = rd.get_raw_ref("user.profile.name")
        self.assertIsInstance(name_ref, Ref)
        self.assertEqual(name_ref.value, "Alice")
        
        # 通过 Ref 修改值
        name_ref.value = "Bob"
        # 使用字典访问验证修改
        user_dict = rd["user"]
        profile_dict = user_dict["profile"]
        self.assertEqual(profile_dict["name"], "Bob")

    def test_get_raw_ref_errors(self) -> None:
        """测试获取 Ref 时的错误情况"""
        data = {"user": {"name": "Alice"}, "count": 5}
        rd: ReactiveDict = ReactiveDict(data)
        
        # 不存在的路径
        with self.assertRaises(KeyError):
            rd.get_raw_ref("nonexistent")
        
        with self.assertRaises(KeyError):
            rd.get_raw_ref("user.nonexistent")
        
        # 尝试在非 ReactiveDict 上继续路径访问
        with self.assertRaises(TypeError):
            rd.get_raw_ref("count.invalid")

    def test_attribute_error(self) -> None:
        """测试属性错误"""
        rd: ReactiveDict = ReactiveDict({"existing": "value"})
        
        with self.assertRaises(AttributeError):
            _ = rd.nonexistent

    def test_reactive_with_effect(self) -> None:
        """测试与 effect 的配合"""
        data = {"counter": 0, "user": {"name": "Alice"}}
        rd: ReactiveDict = ReactiveDict(data)
        
        call_count = 0
        tracked_values = []

        @effect
        def track_counter() -> None:
            nonlocal call_count
            call_count += 1
            tracked_values.append(rd["counter"])

        track_counter()
        self.assertEqual(call_count, 1)
        self.assertEqual(tracked_values[0], 0)

        # 修改值应该触发 effect
        rd["counter"] = 5
        self.assertEqual(call_count, 2)
        self.assertEqual(tracked_values[1], 5)

        rd["counter"] = 10
        self.assertEqual(call_count, 3)
        self.assertEqual(tracked_values[2], 10)

    def test_nested_reactive_with_effect(self) -> None:
        """测试嵌套响应式与 effect 的配合"""
        data = {"user": {"profile": {"score": 100}}}
        rd: ReactiveDict = ReactiveDict(data)
        
        call_count = 0
        tracked_scores = []

        @effect
        def track_score() -> None:
            nonlocal call_count
            call_count += 1
            user_dict = rd["user"]
            profile_dict = user_dict["profile"]
            tracked_scores.append(profile_dict["score"])

        track_score()
        self.assertEqual(call_count, 1)
        self.assertEqual(tracked_scores[0], 100)

        # 修改嵌套值
        user_dict = rd["user"]
        profile_dict = user_dict["profile"]
        profile_dict["score"] = 200
        self.assertEqual(call_count, 2)
        self.assertEqual(tracked_scores[1], 200)

    def test_subscription_through_raw_ref(self) -> None:
        """测试通过原始 Ref 进行订阅"""
        data = {"temperature": 20.0}
        rd: ReactiveDict = ReactiveDict(data)
        
        changes = []

        def on_temp_change(new_val: float, old_val: float) -> None:
            changes.append((old_val, new_val))

        temp_ref = rd.get_raw_ref("temperature")
        temp_ref.subscribe(on_temp_change)
        
        rd["temperature"] = 25.0
        rd["temperature"] = 30.0
        
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0], (20.0, 25.0))
        self.assertEqual(changes[1], (25.0, 30.0))

    def test_complex_data_types(self) -> None:
        """测试复杂数据类型"""
        data = {
            "array": [1, 2, 3],
            "tuple": (4, 5, 6),
            "nested": {
                "list": ["a", "b", "c"],
                "dict": {"x": 1, "y": 2}
            }
        }
        rd: ReactiveDict = ReactiveDict(data)
        
        self.assertEqual(rd["array"], [1, 2, 3])
        self.assertEqual(rd["tuple"], (4, 5, 6))
        nested_dict = rd["nested"]
        self.assertIsInstance(nested_dict, ReactiveDict)
        self.assertEqual(nested_dict["list"], ["a", "b", "c"])
        dict_dict = nested_dict["dict"]
        self.assertIsInstance(dict_dict, ReactiveDict)
        self.assertEqual(dict_dict["x"], 1)
        self.assertEqual(dict_dict["y"], 2)
        
        # 修改复杂类型
        rd["array"] = [7, 8, 9]
        self.assertEqual(rd["array"], [7, 8, 9])

    def test_replacing_nested_dict(self) -> None:
        """测试替换嵌套字典"""
        data = {"config": {"debug": True, "port": 8080}}
        rd: ReactiveDict = ReactiveDict(data)
        
        # 替换整个嵌套字典
        rd["config"] = {"debug": False, "port": 3000, "ssl": True}
        config_dict = rd["config"]
        self.assertIsInstance(config_dict, ReactiveDict)
        self.assertIsInstance(config_dict["debug"], bool)
        self.assertEqual(config_dict["debug"], False)
        self.assertEqual(config_dict["port"], 3000)
        self.assertEqual(config_dict["ssl"], True)


class TestReactiveDictClassMethods(unittest.TestCase):
    """测试 ReactiveDict 的类方法"""

    def test_constructor_from_dict(self) -> None:
        """测试从字典直接创建（构造函数）"""
        data = {"name": "test", "value": 42}
        rd: ReactiveDict = ReactiveDict(data)
        
        self.assertEqual(rd["name"], "test")
        self.assertEqual(rd["value"], 42)

    def test_from_json(self) -> None:
        """测试从 JSON 字符串创建"""
        json_str = '{"user": {"name": "Alice", "age": 30}, "active": true}'
        rd: ReactiveDict = ReactiveDict.from_json(json_str)
        
        user_dict = rd["user"]
        self.assertEqual(user_dict["name"], "Alice")
        self.assertEqual(user_dict["age"], 30)
        self.assertEqual(rd["active"], True)

    def test_from_json_invalid(self) -> None:
        """测试无效 JSON 的情况"""
        # 无效 JSON 格式
        with self.assertRaises(json.JSONDecodeError):
            ReactiveDict.from_json('{"invalid": json}')
        
        # JSON 不是字典
        with self.assertRaises(TypeError):
            ReactiveDict.from_json('["not", "a", "dict"]')


class TestReactiveDictAsync(unittest.IsolatedAsyncioTestCase):
    """ReactiveDict 异步测试"""

    async def test_async_effect_with_reactive_dict(self) -> None:
        """测试异步 effect 与 ReactiveDict 的配合"""
        data = {"status": "idle", "progress": 0}
        rd: ReactiveDict = ReactiveDict(data)
        
        call_count = 0
        tracked_status = []

        @effect
        async def async_track_status() -> None:
            nonlocal call_count
            call_count += 1
            tracked_status.append(rd["status"])
            await asyncio.sleep(0.01)

        await async_track_status()
        self.assertEqual(call_count, 1)
        self.assertEqual(tracked_status[0], "idle")

        rd["status"] = "running"
        await asyncio.sleep(0.1)  # 等待异步回调
        self.assertEqual(call_count, 2)
        self.assertEqual(tracked_status[1], "running")

    async def test_async_subscription_reactive_dict(self) -> None:
        """测试异步订阅 ReactiveDict"""
        data = {"data": {"value": 0}}
        rd: ReactiveDict = ReactiveDict(data)
        
        async_calls = []

        async def async_subscriber(new_val: int, old_val: int) -> None:
            async_calls.append(f"async: {old_val}->{new_val}")
            await asyncio.sleep(0.01)

        value_ref = rd.get_raw_ref("data.value")
        value_ref.subscribe(async_subscriber)
        
        data_dict = rd["data"]
        data_dict["value"] = 10
        await asyncio.sleep(0.1)  # 等待异步回调
        
        self.assertEqual(len(async_calls), 1)
        self.assertEqual(async_calls[0], "async: 0->10")


class TestReactiveDictIntegration(unittest.TestCase):
    """ReactiveDict 集成测试"""

    def test_complex_nested_operations(self) -> None:
        """测试复杂嵌套操作"""
        data = {
            "app": {
                "config": {
                    "database": {"host": "localhost", "port": 5432},
                    "cache": {"enabled": True, "ttl": 3600}
                },
                "state": {
                    "users": {"count": 0, "active": []},
                    "sessions": {}
                }
            }
        }
        rd: ReactiveDict = ReactiveDict(data)
        
        # 深层访问和修改
        app_dict = rd["app"]
        config_dict = app_dict["config"]
        database_dict = config_dict["database"]
        self.assertEqual(database_dict["host"], "localhost")
        database_dict["host"] = "production.db.com"
        self.assertEqual(database_dict["host"], "production.db.com")
        
        # 添加新的嵌套结构
        state_dict = app_dict["state"]
        state_dict["sessions"] = {"session1": {"user_id": 123}}
        sessions_dict = state_dict["sessions"]
        session1_dict = sessions_dict["session1"]
        self.assertEqual(session1_dict["user_id"], 123)
        
        # 验证转换为字典的正确性
        result = rd.to_dict()
        self.assertEqual(result["app"]["config"]["database"]["host"], "production.db.com")
        self.assertEqual(result["app"]["state"]["sessions"]["session1"]["user_id"], 123)

    def test_multiple_effects_same_reactive_dict(self) -> None:
        """测试多个 effects 监听同一个 ReactiveDict"""
        data = {"counter": 0, "multiplier": 2}
        rd: ReactiveDict = ReactiveDict(data)
        
        counter_calls = 0
        multiplier_calls = 0
        product_calls = 0
        
        @effect
        def track_counter() -> None:
            nonlocal counter_calls
            counter_calls += 1
            _ = rd["counter"]
        
        @effect
        def track_multiplier() -> None:
            nonlocal multiplier_calls
            multiplier_calls += 1
            _ = rd["multiplier"]
        
        @effect
        def track_product() -> None:
            nonlocal product_calls
            product_calls += 1
            _ = rd["counter"] * rd["multiplier"]
        
        # 初始调用
        track_counter()
        track_multiplier()
        track_product()
        
        self.assertEqual(counter_calls, 1)
        self.assertEqual(multiplier_calls, 1)
        self.assertEqual(product_calls, 1)
        
        # 修改 counter，应该触发 counter 和 product effects
        rd["counter"] = 5
        self.assertEqual(counter_calls, 2)
        self.assertEqual(multiplier_calls, 1)  # 不变
        self.assertEqual(product_calls, 2)
        
        # 修改 multiplier，应该触发 multiplier 和 product effects
        rd["multiplier"] = 3
        self.assertEqual(counter_calls, 2)  # 不变
        self.assertEqual(multiplier_calls, 2)
        self.assertEqual(product_calls, 3)

    def test_mixed_access_patterns(self) -> None:
        """测试混合访问模式"""
        data = {"user": {"name": "Alice", "settings": {"theme": "dark"}}}
        rd: ReactiveDict = ReactiveDict(data)
        
        # 混合使用括号访问
        user_dict = rd["user"]
        self.assertEqual(user_dict["name"], "Alice")
        settings_dict = user_dict["settings"]
        self.assertEqual(settings_dict["theme"], "dark")
        
        # 混合修改方式
        user_dict["name"] = "Bob"
        settings_dict["theme"] = "light"
        
        self.assertEqual(user_dict["name"], "Bob")
        self.assertEqual(settings_dict["theme"], "light")

    def test_reactive_dict_performance(self) -> None:
        """简单性能测试"""
        # 创建较大的嵌套结构
        data = {}
        for i in range(100):
            data[f"item_{i}"] = {
                "id": i,
                "data": {"value": i * 2, "active": i % 2 == 0}
            }
        
        rd: ReactiveDict = ReactiveDict(data)
        
        # 测试访问性能
        total = 0
        for i in range(100):
            item_dict = rd[f"item_{i}"]
            data_dict = item_dict["data"]
            total += data_dict["value"]
        
        expected_total = sum(i * 2 for i in range(100))
        self.assertEqual(total, expected_total)
        
        # 测试修改性能
        for i in range(50):
            item_dict = rd[f"item_{i}"]
            data_dict = item_dict["data"]
            data_dict["value"] = i * 3
        
        # 验证修改结果
        for i in range(50):
            item_dict = rd[f"item_{i}"]
            data_dict = item_dict["data"]
            self.assertEqual(data_dict["value"], i * 3)


if __name__ == '__main__':
    unittest.main()
