"""将嵌套的字典/JSON数据转换为响应式字典,支持点语法访问和字典风格访问."""
import json
import collections.abc
from cognihub_pyeffectref.ref import Ref
from typing import Any, Dict, Union


class ReactiveDict(collections.abc.MutableMapping):
    """一个通用的响应式字典,能将嵌套的字典/JSON数据转换为Ref包装.

    支持点语法访问和字典风格访问
    """

    def __init__(self, initial_data: Dict[str, Any]):
        """初始化 ReactiveDict."""
        self._data_refs: Dict[str, Ref] = {}
        self._wrap_data(initial_data)

    def _wrap_data(self, data: Dict[str, Any]) -> None:
        """递归地将字典数据包装成 Ref"""
        for key, value in data.items():
            if isinstance(value, dict) and not isinstance(value, ReactiveDict):
                # 递归包装嵌套字典为 ReactiveDict
                self._data_refs[key] = Ref(ReactiveDict(value))
            else:
                self._data_refs[key] = Ref(value)

    def __getattr__(self, name: str) -> Any:
        """支持点语法访问,返回 Ref 的当前值"""
        if name in self._data_refs:
            wrapped_value = self._data_refs[name].value
            # 如果是嵌套的 ReactiveDict,直接返回它本身以便继续点语法访问
            if isinstance(wrapped_value, ReactiveDict):
                return wrapped_value
            return wrapped_value
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        """支持点语法设置值,自动更新Ref"""
        if name in self.__dict__ or name.startswith('_data_refs'):
            # 允许设置 ReactiveDict 自身的属性,或内部的 _data_refs
            super().__setattr__(name, value)
        elif name in self._data_refs:
            # 更新已存在的 Ref
            current_ref_value = self._data_refs[name].value
            if isinstance(current_ref_value, ReactiveDict) and isinstance(value, dict) and not isinstance(value, ReactiveDict):
                # 如果是将字典赋值给嵌套的 ReactiveDict,则更新其内部
                current_ref_value._wrap_data(value)  # 递归更新
            elif isinstance(value, dict) and not isinstance(value, ReactiveDict):
                # 如果新值是字典,但当前 Ref 不是 ReactiveDict,则替换为新的 ReactiveDict Ref
                self._data_refs[name].value = ReactiveDict(value)
            else:
                self._data_refs[name].value = value
        else:
            # 添加新的 Ref
            if isinstance(value, dict) and not isinstance(value, ReactiveDict):
                self._data_refs[name] = Ref(ReactiveDict(value))
            else:
                self._data_refs[name] = Ref(value)

    def __getitem__(self, key: str) -> Any:
        """支持字典风格访问,返回 Ref 的当前值"""
        if key in self._data_refs:
            wrapped_value = self._data_refs[key].value
            # 如果是嵌套的 ReactiveDict,直接返回它本身以便继续点语法访问
            if isinstance(wrapped_value, ReactiveDict):
                return wrapped_value
            return wrapped_value
        raise KeyError(f"'{key}' not found in ReactiveDict.")

    def __setitem__(self, key: str, value: Any) -> None:
        """支持字典风格设置值,自动更新 Ref"""
        self.__setattr__(key, value)

    def __delitem__(self, key: str) -> None:
        """支持删除,移除 Ref"""
        if key in self._data_refs:
            del self._data_refs[key]
        else:
            raise KeyError(f"'{key}' not found in ReactiveDict.")

    def __len__(self) -> int:
        return len(self._data_refs)

    def __iter__(self) -> collections.abc.Iterator[str]:
        return iter(self._data_refs)

    def __contains__(self, key: object) -> bool:
        """支持 'in' 操作符"""
        return key in self._data_refs

    def to_dict(self) -> Dict[str, Any]:
        """将 ReactiveDict 转换为普通字典(调用时的拷贝)"""
        result = {}
        for key, ref in self._data_refs.items():
            value = ref.value
            if isinstance(value, ReactiveDict):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    def get_raw_ref(self, key_path: str) -> Ref:
        """通过点分隔路径获取底层 Ref 实例

        例如: get_raw_ref('nested_key.item')
        这是主程序修改数据或进行高级订阅的接口
        """
        parts = key_path.split('.')
        current_data: Union[ReactiveDict, Any] = self
        for i, part in enumerate(parts):
            if isinstance(current_data, ReactiveDict):
                if part not in current_data._data_refs:
                    raise KeyError(f"Path '{key_path}' not found at part '{part}'.")

                if i == len(parts) - 1:
                    return current_data._data_refs[part]
                else:
                    # 沿着路径向下,获取 Ref 包装的值(可能是另一个 ReactiveDict)
                    current_data = current_data._data_refs[part].value
            else:
                raise TypeError(f"'{'.'.join(parts[:i])}' is not a ReactiveDict, cannot get '{part}'.")
        raise ValueError(f"Invalid key_path: {key_path}")  # 应该不会到达这里

    @classmethod
    def from_json(cls, json_string: str) -> 'ReactiveDict':
        """从 JSON 字符串创建 ReactiveDict"""
        data = json.loads(json_string)
        if not isinstance(data, dict):
            raise TypeError("JSON string must represent a dictionary.")
        return cls(data)

