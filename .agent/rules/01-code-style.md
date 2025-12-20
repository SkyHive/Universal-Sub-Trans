---
trigger: always_on
---

# Python 项目规则 (Python Project Rules)

## 1. 环境与依赖 (Environment & Dependencies)

* **Python 版本**: 本项目使用 Python 3.10+。
* **虚拟环境**: 所有开发必须在 `.venv` 虚拟环境中进行。
* **依赖管理**:
  * 优先使用 `pyproject.toml` (配合 uv)。
  * **现有项目**:
    * 如果使用 `requirements.txt`，必须包含 `requirements-dev.txt` 用于开发依赖
    * 鼓励逐步迁移到 `pyproject.toml`
  * **依赖锁定**: 必须提供锁文件 (`poetry.lock`, `pdm.lock`, 或 `requirements.txt` 的固定版本)

## 2. 代码风格与质量 (Code Style & Quality)

* **格式化**: 严格使用 `black` 进行代码格式化。
* **Linter**: 使用 `flake8` + 可选 `pylint` 用于复杂项目
* **Import 排序**: 严格使用 `isort` 进行 import 语句排序。
* **类型检查**: 推荐使用 `mypy` 或 `pyright` 进行静态类型检查
* **配置**: AI 必须遵守项目根目录下的 `pyproject.toml`, `.flake8rc`, 或 `.isort.cfg` 中的所有规则。

## 3. 类型提示 (Type Hinting)

* **强制要求**: 所有**新编写**的函数和类方法都**必须**包含完整的类型提示 (Type Hints)。
* **标准**: 使用 `typing` 模块提供的标准类型（例如 `list`, `dict`, `Optional`, `Union`）。
* **返回值**: 即使函数没有返回值，也必须明确注解为 `-> None`。
* **复杂类型**: 推荐使用 Python 3.9+ 的内置泛型 (`list[str]` 而非 `List[str]`)
* **严格模式**: 对于新模块，考虑使用 `from __future__ import annotations`

## 4. 文档字符串 (Docstrings)

* **强制要求**: 所有的公共模块 (public modules)、类 (classes) 和函数 (functions) **必须**包含文档字符串 (Docstrings)。
* **格式**: 统一使用 **Google 风格** 的 Docstrings。
  * 示例:

      ```python
      def my_function(arg1: str, arg2: int) -> bool:
          """
          这是一个函数功能的简短描述。
      
          Args:
              arg1 (str): 参数1的描述。
              arg2 (int): 参数2的描述。
      
          Returns:
              bool: 返回值的描述。
          """
          # ...
      ```

## 5. 测试 (Testing)

* **框架**: 必须使用 `pytest` 编写所有单元测试。
* **文件结构**: 测试文件必须放在 `tests/` 目录下，并以 `test_` 开头 (例如 `tests/test_utils.py`)。
* **新功能**: 在实现新功能时，必须为其编写相应的单元测试。

## 6. 核心禁止事项 (Strict Prohibitions)

* **禁止 `print`**: 在库代码或业务逻辑中**禁止**使用 `print()` 语句。请使用 `logging` 模块进行日志记录。
* **禁止宽泛的异常**: **禁止**使用宽泛的异常捕获，如 `except:` 或 `except Exception:`。必须捕获具体的异常类型 (例如 `except ValueError:`)。
* **禁止魔法字符串 (Magic Strings)**: 不要硬编码重复出现的字符串（例如配置键、状态名）。应将它们定义为模块顶层的常量。

## 7. 配置管理 (Configuration Management)

* **环境配置**: 使用环境变量进行配置，通过 `pydantic-settings` 或 `python-dotenv` 管理
* **敏感信息**: 禁止在代码中硬编码密码、API密钥等敏感信息
* **配置验证**: 应用启动时应验证必要配置项的完整性
