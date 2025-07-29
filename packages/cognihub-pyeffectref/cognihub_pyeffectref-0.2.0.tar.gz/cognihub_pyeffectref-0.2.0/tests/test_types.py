"""类型提示和类型安全测试"""
import unittest
import sys
import os
from typing import List, Dict, Optional, Union

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref import Ref, effect


class TestTypeHints(unittest.TestCase):
    """类型提示测试"""

    def test_basic_type_annotations(self) -> None:
        """测试基本类型注解"""
        # 基础类型
        int_ref: Ref[int] = Ref(42)
        str_ref: Ref[str] = Ref("hello")
        bool_ref: Ref[bool] = Ref(True)
        float_ref: Ref[float] = Ref(3.14)
        
        self.assertEqual(int_ref.value, 42)
        self.assertEqual(str_ref.value, "hello")
        self.assertEqual(bool_ref.value, True)
        self.assertEqual(float_ref.value, 3.14)

    def test_collection_type_annotations(self) -> None:
        """测试集合类型注解"""
        # 列表类型
        list_ref: Ref[List[int]] = Ref([1, 2, 3])
        self.assertEqual(list_ref.value, [1, 2, 3])
        
        # 字典类型
        dict_ref: Ref[Dict[str, int]] = Ref({"a": 1, "b": 2})
        self.assertEqual(dict_ref.value, {"a": 1, "b": 2})
        
        # 嵌套类型
        nested_ref: Ref[List[Dict[str, int]]] = Ref([{"x": 1}, {"y": 2}])
        self.assertEqual(nested_ref.value, [{"x": 1}, {"y": 2}])

    def test_optional_type_annotations(self) -> None:
        """测试可选类型注解"""
        optional_ref: Ref[Optional[str]] = Ref(None)
        self.assertIsNone(optional_ref.value)
        
        optional_ref.value = "not none"
        self.assertEqual(optional_ref.value, "not none")
        
        optional_ref.value = None
        self.assertIsNone(optional_ref.value)

    def test_union_type_annotations(self) -> None:
        """测试联合类型注解"""
        union_ref: Ref[Union[int, str]] = Ref(42)
        self.assertEqual(union_ref.value, 42)
        
        union_ref.value = "string value"
        self.assertEqual(union_ref.value, "string value")

    def test_custom_class_type_annotations(self) -> None:
        """测试自定义类的类型注解"""
        class Person:
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age
            
            def __eq__(self, other: object) -> bool:
                if not isinstance(other, Person):
                    return False
                return self.name == other.name and self.age == other.age
        
        person_ref: Ref[Person] = Ref(Person("Alice", 30))
        self.assertEqual(person_ref.value.name, "Alice")
        self.assertEqual(person_ref.value.age, 30)
        
        person_ref.value = Person("Bob", 25)
        self.assertEqual(person_ref.value.name, "Bob")
        self.assertEqual(person_ref.value.age, 25)

    def test_effect_type_annotations(self) -> None:
        """测试 effect 的类型注解"""
        counter: Ref[int] = Ref(0)
        result_list: List[int] = []
        
        @effect
        def typed_effect() -> None:
            result_list.append(counter.value)
        
        @effect
        def effect_with_return() -> int:
            return counter.value * 2
        
        typed_effect()
        self.assertEqual(len(result_list), 1)
        self.assertEqual(result_list[0], 0)
        
        result = effect_with_return()
        self.assertEqual(result, 0)
        
        counter.value = 5
        self.assertEqual(len(result_list), 2)
        self.assertEqual(result_list[1], 5)

    def test_callback_type_annotations(self) -> None:
        """测试回调函数的类型注解"""
        str_ref: Ref[str] = Ref("initial")
        changes: List[tuple[str, str]] = []
        
        def typed_callback(new_value: str, old_value: str) -> None:
            changes.append((old_value, new_value))
        
        str_ref.subscribe(typed_callback)
        str_ref.value = "changed"
        
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0], ("initial", "changed"))

    def test_generic_consistency(self) -> None:
        """测试泛型一致性"""
        # 确保类型参数在整个操作过程中保持一致
        numbers: Ref[List[int]] = Ref([1, 2, 3])
        
        def process_numbers(new_nums: List[int], old_nums: List[int]) -> None:
            # 这里的类型应该与 Ref 的类型参数一致
            self.assertIsInstance(new_nums, list)
            self.assertIsInstance(old_nums, list)
            for num in new_nums + old_nums:
                self.assertIsInstance(num, int)
        
        numbers.subscribe(process_numbers)
        numbers.value = [4, 5, 6]

    def test_type_inference(self) -> None:
        """测试类型推断"""
        # 不显式指定类型，让 Python 推断
        auto_ref = Ref("auto inferred")
        self.assertEqual(auto_ref.value, "auto inferred")
        
        # 修改为相同类型应该工作
        auto_ref.value = "changed value"
        self.assertEqual(auto_ref.value, "changed value")


class TestTypeCompatibility(unittest.TestCase):
    """类型兼容性测试"""

    def test_ref_subclass_compatibility(self) -> None:
        """测试 Ref 与子类的兼容性"""
        class Number:
            def __init__(self, value: int):
                self.value = value
        
        class Integer(Number):
            pass
        
        # 应该能够存储子类实例
        number_ref: Ref[Number] = Ref(Integer(42))
        self.assertEqual(number_ref.value.value, 42)

    def test_callback_parameter_compatibility(self) -> None:
        """测试回调参数兼容性"""
        ref: Ref[int] = Ref(0)
        
        # 不同的回调签名应该都能工作
        def strict_callback(new_val: int, old_val: int) -> None:
            pass
        
        def flexible_callback(new_val: object, old_val: object) -> None:
            pass
        
        ref.subscribe(strict_callback)
        ref.subscribe(flexible_callback)
        
        ref.value = 42  # 应该不抛出类型错误


if __name__ == '__main__':
    unittest.main()
