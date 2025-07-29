# CogniHub PyEffectRef

CogniHub 项目的响应式编程库,提供类似 Vue 3 Composition API 的响应式系统.本库分为**底层接口**和**高级接口**两个层次,满足不同复杂度的使用需求.

## 特性

- 🔄 **响应式编程**: 类似 Vue 3 Composition API 的响应式系统
- 🔒 **线程安全**: 支持多线程环境下的安全操作  
- ⚡ **异步支持**: 完整支持 asyncio 协程环境
- 🎯 **类型提示**: 完整的 TypeScript 风格类型提示支持
- 🏗️ **分层设计**: 底层接口(Ref/effect) + 高级接口(ReactiveDict/ReadOnlyView)
- 🎛️ **执行控制**: 支持同步、异步、顺序执行等多种模式

## 安装

```bash
pip install cognihub-pyeffectref
```

或从源码安装：

```bash
git clone https://github.com/hsz1273327/cognihub_pyeffectref.git
cd cognihub_pyeffectref
pip install -e .
```

## 📚 架构概览

本库采用分层设计,提供两个层次的接口：

### 🔧 底层接口 (Low-level APIs)

- **`Ref[T]`**: 响应式数据容器,支持泛型类型指定
- **`effect`**: 副作用装饰器,自动追踪依赖关系
- **`ReadOnlyRef[T]`**: 只读响应式引用

**特点**: 直接使用泛型指定类型,适合简单数据结构和性能敏感场景

### 🏗️ 高级接口 (High-level APIs)

- **`ReactiveDict`**: 响应式字典,支持嵌套结构,配合 TypedDict 和 cast 使用
- **`ReadOnlyView`**: 只读视图,配合 Protocol 和 cast 使用

**特点**: 需要结合 `TypedDict` 和 `Protocol` 指定复杂类型结构,适合复杂应用场景

## 🚀 快速开始

### 1️⃣ 底层接口示例

#### 基本用法 - 泛型类型指定

```python
from cognihub_pyeffectref import Ref, effect
from typing import List, Dict

# 使用泛型指定类型
count: Ref[int] = Ref(0)
name: Ref[str] = Ref("Alice") 
items: Ref[List[str]] = Ref(["apple", "banana"])

# 创建副作用函数
@effect
def log_count() -> None:
    print(f"Count is: {count.value}")

@effect  
def log_greeting() -> None:
    print(f"Hello, {name.value}!")

# 初始执行
log_count()      # 输出: Count is: 0
log_greeting()   # 输出: Hello, Alice!

# 修改数据,自动触发副作用
count.value = 5        # 输出: Count is: 5
name.value = "Bob"     # 输出: Hello, Bob!
```

#### 同步/异步/多线程支持

默认单线程同步执行,通过`Ref.configure_sync_task_executor`可配置为异步或多线程执行.

**注意:**

1. 请仅在需要时使用异步或多线程,因为这会增加复杂性和调试难度.
2. 仅在应用入口处设置一次执行器配置即可,不需要在每个模块中重复设置.设置接口是一次性的,一旦设置过了就无法改变

```python
import asyncio
import threading
import time
from cognihub_pyeffectref import Ref, effect

data: Ref[str] = Ref("initial")

# 1. 同步使用
@effect
def sync_effect() -> None:
    print(f"Sync effect: {data.value}")

# 2. 异步使用  
@effect
async def async_effect() -> None:
    print(f"Async effect: {data.value}")
    await asyncio.sleep(0.1)  # 异步操作

# 3. 多线程使用
def thread_worker(thread_id: int) -> None:
    @effect
    def thread_effect() -> None:
        print(f"Thread {thread_id} effect: {data.value}")
    
    thread_effect()  # 建立依赖
    time.sleep(0.1)

async def main():
    # 同步执行
    sync_effect()
    
    # 异步执行  
    await async_effect()
    
    # 多线程执行
    threads = []
    for i in range(3):
        thread = threading.Thread(target=thread_worker, args=(i,))
        thread.start()
        threads.append(thread)
    
    # 触发所有副作用
    data.value = "updated"
    await asyncio.sleep(0.2)  # 等待异步和线程完成
    
    for thread in threads:
        thread.join()

# asyncio.run(main())
```

#### 执行器配置 - 控制回调执行方式

> 默认的回调执行方式:

1. 在未设置执行器时
   1. 同步回调在当前线程同步执行.
   2. 异步回调在 asyncio 事件循环中异步执行.

2. 在设置了执行器的情况下
   1. 同步回调会在执行器中多线程后台执行.
   2. 异步回调会在 asyncio 事件循环中异步执行.

> 实例的精细化回调执行控制

实例可以在初始化时额外指定其用`subscribe`注册的同步回调函数的执行方式.

1. `subscribe_immediate=True`: 强制在当前线程同步执行回调,忽略全局执行器配置.
2. `subscribe_sequential=True`: 保证同步回调函数按注册顺序在后台执行,适用于需要顺序执行的场景.

```python
import concurrent.futures
from cognihub_pyeffectref import Ref

# 配置全局执行器 - 使用 asyncio 线程池
Ref.configure_sync_task_executor('asyncio')

# 或使用自定义线程池
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
Ref.configure_sync_task_executor(executor)

# 强制立即同步执行 (忽略执行器配置)
immediate_ref = Ref(0, subscribe_immediate=True)

# 保证顺序执行 (在执行器中按顺序执行)
sequential_ref = Ref(0, subscribe_sequential=True)
```

### 2️⃣ 高级接口示例

#### ReactiveDict - 结合 TypedDict 指定结构

```python
from cognihub_pyeffectref import ReactiveDict, effect
from typing import TypedDict, cast

# 1. 定义数据结构
class UserData(TypedDict):
    name: str
    email: str  
    age: int
    is_active: bool

# 2. 创建响应式字典
user_dict = ReactiveDict({
    'name': 'Alice',
    'email': 'alice@example.com', 
    'age': 25,
    'is_active': True
})

# 3. 类型转换以获得类型提示
user: UserData = cast(UserData, user_dict)

# 4. 使用时享受完整类型提示
@effect
def watch_user() -> None:
    print(f"User: {user['name']} ({user['age']})")
    print(f"Email: {user['email']}")
    print(f"Active: {user['is_active']}")

watch_user()

# 5. 修改数据
user['name'] = 'Bob'      # 自动触发副作用
user['age'] = 26          # 自动触发副作用
```

#### ReadOnlyView - 结合 Protocol 创建只读视图

```python
from cognihub_pyeffectref import ReactiveDict, ReadOnlyView, ReadOnlyRef, effect
from typing import Protocol, cast, Any

# 1. 定义 Protocol 描述只读视图结构
class UserViewProtocol(Protocol):
    name: ReadOnlyRef[str]
    email: ReadOnlyRef[str] 
    age: ReadOnlyRef[int]
    is_active: ReadOnlyRef[bool]
    
    def __call__(self) -> dict[str, Any]: ...

# 2. 创建原始数据
user_data = ReactiveDict({
    'name': 'Alice',
    'email': 'alice@example.com',
    'age': 25, 
    'is_active': True
})

# 3. 创建只读视图
user_view = cast(UserViewProtocol, ReadOnlyView(user_data))

# 4. 只读访问 - 享受完整类型提示和防护
@effect  
def watch_user_view() -> None:
    print(f"Name: {user_view.name.value}")
    print(f"Email: {user_view.email.value}")
    print(f"Age: {user_view.age.value}")

watch_user_view()

# 5. 无法修改 (编译时和运行时都会报错)
# user_view.name.value = "Bob"     # AttributeError: ReadOnlyRef has no setter
# user_view['name'] = "Bob"        # TypeError: ReadOnlyView is not subscriptable

# 6. 只能通过原始数据修改
user_data.name = "Bob"  # 自动触发只读视图的副作用
```

#### 复杂嵌套数据结构

```python
from cognihub_pyeffectref import ReactiveDict, ReadOnlyView, ReadOnlyRef, effect
from typing import Protocol, cast, Any

# 1. 定义嵌套的 Protocol 结构
class DatabaseConfig(Protocol):
    host: ReadOnlyRef[str]
    port: ReadOnlyRef[int]
    name: ReadOnlyRef[str]

class ApiConfig(Protocol):  
    base_url: ReadOnlyRef[str]
    timeout: ReadOnlyRef[int]
    retry_count: ReadOnlyRef[int]

class AppConfig(Protocol):
    database: DatabaseConfig
    api: ApiConfig
    debug_mode: ReadOnlyRef[bool]
    
    def __call__(self) -> dict[str, Any]: ...

# 2. 创建嵌套数据
config_data = ReactiveDict({
    'database': {
        'host': 'localhost',
        'port': 5432,
        'name': 'myapp'
    },
    'api': {
        'base_url': 'https://api.example.com',
        'timeout': 30,
        'retry_count': 3
    },
    'debug_mode': False
})

# 3. 创建类型化的只读视图
config_view = cast(AppConfig, ReadOnlyView(config_data))

# 4. 访问嵌套数据 - 完整类型提示
@effect
def watch_config() -> None:
    db_host = config_view.database.host.value
    api_url = config_view.api.base_url.value  
    debug = config_view.debug_mode.value
    
    print(f"Database: {db_host}")
    print(f"API: {api_url}")
    print(f"Debug: {debug}")

watch_config()

# 5. 修改原始数据触发变更
config_data.database.host = 'production-db'
config_data.debug_mode = True
```

## 📖 API 参考

### 🔧 底层接口 (Low-level APIs)

#### Ref[T]

响应式数据容器类,支持泛型类型指定.

**构造函数**

- `Ref(initial_value: T, subscribe_immediate: bool = False, subscribe_sequential: bool = False)`
  - `initial_value`: 初始值
  - `subscribe_immediate`: 是否强制在当前线程同步执行回调 (忽略全局执行器配置)
  - `subscribe_sequential`: 是否保证回调按注册顺序执行

**属性**

- `value: T`: 获取或设置引用的值

**方法**

- `subscribe(callback: Callable[[T, T], None])`: 订阅值变化
- `unsubscribe(callback: Callable[[T, T], None])`: 取消订阅
- `configure_sync_task_executor(executor)`: 配置全局同步任务执行器

**类方法**

- `Ref.configure_sync_task_executor('asyncio' | ThreadPoolExecutor)`: 配置全局执行器

#### ReadOnlyRef[T] 

只读响应式引用,从 Ref 创建.

**构造函数**

- `ReadOnlyRef(ref: Ref[T])`: 从现有 Ref 创建只读引用

**属性**

- `value: T`: 只读访问引用的值 (无 setter)

**方法**

- `subscribe(callback: Callable[[T, T], None])`: 订阅值变化
- `unsubscribe(callback: Callable[[T, T], None])`: 取消订阅

#### effect

副作用装饰器,自动追踪 Ref 依赖关系.

```python
@effect
def my_effect() -> None:
    # 访问 Ref.value 会自动建立依赖关系
    pass

# 或手动调用
effect_wrapper = effect(my_function)
effect_wrapper()
```

#### EffectWrapper

effect 装饰器返回的包装器类.

**方法**

- `stop()`: 停止副作用,使其不再响应数据变化

### 🏗️ 高级接口 (High-level APIs)

#### ReactiveDict

响应式字典,支持嵌套结构和动态键.

**构造函数**

- `ReactiveDict(initial_data: dict = None)`: 创建响应式字典

**方法**

- `to_dict() -> dict`: 转换为普通字典
- `keys()`, `values()`, `items()`: 字典接口方法
- `get(key, default=None)`: 获取值
- `pop(key, default=None)`: 删除并返回值
- `clear()`: 清空字典
- `update(other)`: 更新字典

**特性**

- 支持嵌套结构自动转换为 ReactiveDict
- 动态属性访问: `obj.key` 等价于 `obj['key']`
- 与 TypedDict 结合使用获得类型提示

#### ReadOnlyView

只读视图,从 ReactiveDict 创建结构化的只读访问.

**构造函数**

- `ReadOnlyView(reactive_dict: ReactiveDict)`: 创建只读视图

**特性**

- 递归将所有值转换为 ReadOnlyRef
- 支持嵌套结构的只读访问  
- 与 Protocol 结合获得完整类型提示
- 调用 `view()` 返回当前状态的字典快照

**使用模式**

```python
# 1. 定义结构 Protocol
class MyDataProtocol(Protocol):
    field: ReadOnlyRef[str]
    def __call__(self) -> dict[str, Any]: ...

# 2. 创建并转换
data = ReactiveDict({'field': 'value'})
view = cast(MyDataProtocol, ReadOnlyView(data))

# 3. 类型安全访问
print(view.field.value)  # 完整类型提示
snapshot = view()        # 获取当前状态快照
```

## ⚡ 执行模式详解

### 同步执行 (默认)

```python
from cognihub_pyeffectref import Ref, effect

# 默认模式：回调在当前线程中执行
data = Ref("initial")

@effect
def sync_effect() -> None:
    print(f"Current value: {data.value}")

sync_effect()  # 立即执行
data.value = "changed"  # 在当前线程中触发回调
```

### 异步执行 (asyncio 环境)

```python
import asyncio
from cognihub_pyeffectref import Ref, effect

# 配置使用 asyncio 线程池
Ref.configure_sync_task_executor('asyncio')

data = Ref("initial")

@effect
async def async_effect() -> None:
    print(f"Async value: {data.value}")
    await asyncio.sleep(0.1)

async def main():
    await async_effect()  # 建立依赖
    data.value = "changed"  # 回调将在 asyncio.to_thread 中执行
    await asyncio.sleep(0.2)  # 等待异步回调完成

asyncio.run(main())
```

### 多线程执行

```python
import threading
import concurrent.futures
from cognihub_pyeffectref import Ref, effect

# 配置自定义线程池
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
Ref.configure_sync_task_executor(executor)

data = Ref(0)

@effect
def thread_effect() -> None:
    thread_id = threading.get_ident()
    value = data.value
    print(f"Thread {thread_id}: {value}")

# 在多个线程中建立依赖
threads = []
for i in range(3):
    thread = threading.Thread(target=thread_effect)
    thread.start()
    threads.append(thread)

# 触发回调 - 将在线程池中执行
data.value = 42

for thread in threads:
    thread.join()
    
executor.shutdown(wait=True)
```

### 执行控制选项

```python
from cognihub_pyeffectref import Ref

# 1. 强制立即同步执行 (忽略全局执行器)
immediate_ref = Ref(0, subscribe_immediate=True)

# 2. 保证顺序执行 (在执行器中按注册顺序执行)  
sequential_ref = Ref(0, subscribe_sequential=True)

# 3. 组合使用 (immediate 优先级更高)
combined_ref = Ref(0, subscribe_immediate=True, subscribe_sequential=True)
```

## 🔒 线程安全特性

本库在设计时充分考虑了线程安全：

### 内部锁机制

- `Ref` 使用内部锁保护订阅者集合的并发修改
- 支持在多线程环境中安全地读写响应式数据
- `ReactiveDict` 的嵌套操作也是线程安全的

### 上下文隔离

- 异步环境使用 `contextvars` 隔离 effect 上下文
- 多线程环境使用 `threading.local` 进行线程隔离
- 确保副作用函数在正确的上下文中执行

### 执行器配置

- 全局执行器配置支持 `'asyncio'` 和自定义 `ThreadPoolExecutor`
- `subscribe_immediate=True` 可强制在当前线程同步执行,提供确定性行为
- `subscribe_sequential=True` 保证回调按注册顺序执行,避免竞态条件

## 🎯 使用场景推荐

### 何时使用底层接口 (Ref/effect)

✅ **适合场景**:

- 简单的响应式状态管理
- 性能敏感的应用
- 需要精确控制执行时机
- 与现有代码集成

```python
# 适合：简单计数器
counter: Ref[int] = Ref(0)
user_name: Ref[str] = Ref("Anonymous")
```

### 何时使用高级接口 (ReactiveDict/ReadOnlyView)

✅ **适合场景**:

- 复杂的嵌套数据结构
- 需要结构化的数据访问
- 配置管理系统
- 大型应用的状态管理

```python
# 适合：复杂配置对象
app_config = ReactiveDict({
    'database': {'host': 'localhost', 'port': 5432},
    'cache': {'ttl': 3600, 'max_size': 1000},
    'features': {'debug': False, 'analytics': True}
})
```

### 混合使用模式

```python
# 组合使用：底层接口处理核心状态,高级接口管理配置
from cognihub_pyeffectref import Ref, ReactiveDict, ReadOnlyView, effect
from typing import Protocol, cast

# 底层：核心应用状态
app_state: Ref[str] = Ref("initializing")
user_count: Ref[int] = Ref(0)

# 高级：复杂配置管理
config_data = ReactiveDict({
    'ui': {'theme': 'dark', 'language': 'en'},
    'api': {'timeout': 30, 'retries': 3}
})

class ConfigProtocol(Protocol):
    ui: dict[str, str]
    api: dict[str, int]

config = cast(ConfigProtocol, config_data)

@effect
def sync_state() -> None:
    state = app_state.value
    theme = config['ui']['theme']
    print(f"App {state} with {theme} theme")

sync_state()
```

## 🛠️ 开发指南

### 环境设置

```bash
# 克隆仓库
git clone https://github.com/hsz1273327/cognihub_pyeffectref.git
cd cognihub_pyeffectref

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=cognihub_pyeffectref --cov-report=html

# 运行特定测试文件
pytest tests/test_ref.py -v
```

### 代码质量检查

```bash
# 格式化代码
black .
isort .

# 类型检查
mypy cognihub_pyeffectref

# 代码风格检查
flake8 cognihub_pyeffectref
```

### 项目结构

```
cognihub_pyeffectref/
├── cognihub_pyeffectref/    # 主要源码
│   ├── __init__.py         # 公共接口导出
│   ├── ref.py              # 底层接口：Ref, ReadOnlyRef
│   ├── effect.py           # effect 装饰器和 EffectWrapper
│   ├── reactive_dict.py    # 高级接口：ReactiveDict
│   └── local.py            # 上下文管理（threading.local 等）
├── tests/                  # 测试文件
│   ├── test_ref.py         # Ref 相关测试
│   ├── test_effect.py      # effect 相关测试
│   └── test_reactive_dict.py # ReactiveDict 相关测试
├── examples/               # 使用示例
└── docs/                   # 文档
```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下流程：

### 开发流程

1. **Fork 项目**并创建功能分支
2. **编写代码**并确保测试通过
3. **添加测试**覆盖新功能
4. **更新文档**如有必要
5. **提交 Pull Request**

### 代码规范

- 使用 **类型提示** (`typing` 模块)
- 遵循 **PEP 8** 代码风格
- 编写 **docstring** 描述函数和类
- 保持 **测试覆盖率** > 90%
- 确保所有测试通过

### 提交信息规范

使用语义化提交信息：

```bash
feat: 添加新功能
fix: 修复 bug  
docs: 更新文档
test: 添加测试
refactor: 重构代码
style: 代码格式调整
```

### Issue 和 PR 模板

- **Bug 报告**: 提供复现步骤、预期行为、实际行为
- **功能请求**: 描述用例、期望 API、实现建议
- **Pull Request**: 关联 Issue、说明变更、添加测试

## 📄 许可证

本项目采用 MIT 许可证.详见 [LICENSE](LICENSE) 文件.

## 📚 相关资源

- **GitHub**: [cognihub_pyeffectref](https://github.com/hsz1273327/cognihub_pyeffectref)
- **PyPI**: [cognihub-pyeffectref](https://pypi.org/project/cognihub-pyeffectref/)
- **示例**: [examples/](https://github.com/hsz1273327/cognihub_pyeffectref/tree/master/examples)

## 🔄 变更日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解完整变更历史.

---

**感谢使用 CogniHub PyEffectRef！** 🚀

如有问题或建议,欢迎提交 [Issue](https://github.com/hsz1273327/cognihub_pyeffectref/issues) 或参与讨论.
