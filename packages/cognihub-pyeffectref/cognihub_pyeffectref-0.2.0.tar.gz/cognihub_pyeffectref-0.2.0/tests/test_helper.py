"""helper.py 模块的测试"""
from cognihub_pyeffectref.helper import create_actions_dict
import unittest
import warnings
import sys
import os
from typing import Callable, Any, List

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCreateActionsDict(unittest.TestCase):
    """测试 create_actions_dict 函数"""

    def test_basic_function_list_to_dict(self) -> None:
        """测试基本的函数列表转换为字典"""
        def func1() -> str:
            return "result1"

        def func2() -> str:
            return "result2"

        def func3() -> str:
            return "result3"
        functions: List[Callable[..., Any]] = [func1, func2, func3]
        result = create_actions_dict(functions)
        result = create_actions_dict(functions)

        # 检查结果字典
        self.assertEqual(len(result), 3)
        self.assertIn("func1", result)
        self.assertIn("func2", result)
        self.assertIn("func3", result)

        # 检查函数是否正确映射
        self.assertIs(result["func1"], func1)
        self.assertIs(result["func2"], func2)
        self.assertIs(result["func3"], func3)

        # 检查函数是否可调用
        self.assertEqual(result["func1"](), "result1")
        self.assertEqual(result["func2"](), "result2")
        self.assertEqual(result["func3"](), "result3")

    def test_functions_with_parameters(self) -> None:
        """测试带参数的函数"""
        def add(a: int, b: int) -> int:
            return a + b

        def multiply(x: float, y: float) -> float:
            return x * y

        def greet(name: str, prefix: str = "Hello") -> str:
            return f"{prefix}, {name}!"
        functions: List[Callable[..., Any]] = [add, multiply, greet]
        result = create_actions_dict(functions)
        result = create_actions_dict(functions)

        self.assertEqual(len(result), 3)

        # 测试带参数的函数调用
        self.assertEqual(result["add"](3, 4), 7)
        self.assertEqual(result["multiply"](2.5, 4.0), 10.0)
        self.assertEqual(result["greet"]("Alice"), "Hello, Alice!")
        self.assertEqual(result["greet"]("Bob", "Hi"), "Hi, Bob!")

    def test_empty_function_list(self) -> None:
        result = create_actions_dict([])
        self.assertEqual(result, {})

    def test_single_function(self) -> None:
        """测试单个函数"""
        def single_func() -> str:
            return "single"
        result = create_actions_dict([single_func])

        self.assertEqual(len(result), 1)
        self.assertIn("single_func", result)
        self.assertEqual(result["single_func"](), "single")

    def test_lambda_function_warning(self) -> None:
        """测试lambda函数会产生警告并被跳过"""
        def normal_func() -> str:
            return "normal"

        functions: List[Callable[..., Any]] = [normal_func, lambda: "lambda"]

        # 捕获警告
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = create_actions_dict(functions)

            # 检查警告
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, UserWarning))
            self.assertIn("匿名", str(w[0].message))

        # 检查结果：只包含普通函数
        self.assertEqual(len(result), 1)
        self.assertIn("normal_func", result)
        self.assertNotIn("<lambda>", result)

    def test_non_callable_object_warning(self) -> None:
        """测试非可调用对象会产生警告并被跳过"""
        def valid_func() -> str:
            return "valid"

        non_callable = "not a function"
        another_non_callable = 42
        functions: list = [valid_func, non_callable, another_non_callable]

        # 捕获警告
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = create_actions_dict(functions)

            # 检查警告数量
            self.assertEqual(len(w), 2)

            # 检查警告内容
            for warning in w:
                self.assertTrue(issubclass(warning.category, UserWarning))
                self.assertIn("不是可调用对象", str(warning.message))

        # 检查结果：只包含有效函数
        self.assertEqual(len(result), 1)
        self.assertIn("valid_func", result)

    def test_mixed_valid_and_invalid_functions(self) -> None:
        """测试混合有效和无效函数的情况"""
        def func1() -> str:
            return "func1"

        def func2() -> str:
            return "func2"


        non_callable = "string"
        functions: list = [func1, lambda x:x * 2, func2, non_callable]

        # 捕获警告
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = create_actions_dict(functions)

            # 应该有2个警告
            self.assertEqual(len(w), 2)

        # 检查结果：只包含有效的命名函数
        self.assertEqual(len(result), 2)
        self.assertIn("func1", result)
        self.assertIn("func2", result)
        self.assertEqual(result["func1"](), "func1")
        self.assertEqual(result["func2"](), "func2")

    def test_class_methods(self) -> None:
        """测试类方法"""
        class TestClass:
            def method1(self) -> str:
                return "method1"

            @staticmethod
            def static_method() -> str:
                return "static"

            @classmethod
            def class_method(cls) -> str:
                return "class"

        instance = TestClass()
        functions: List[Callable[..., Any]] = [instance.method1, TestClass.static_method, TestClass.class_method]
        result = create_actions_dict(functions)
        result = create_actions_dict(functions)

        self.assertEqual(len(result), 3)
        self.assertIn("method1", result)
        self.assertIn("static_method", result)
        self.assertIn("class_method", result)

        # 测试调用
        self.assertEqual(result["method1"](), "method1")
        self.assertEqual(result["static_method"](), "static")
        self.assertEqual(result["class_method"](), "class")


if __name__ == '__main__':
    unittest.main()
