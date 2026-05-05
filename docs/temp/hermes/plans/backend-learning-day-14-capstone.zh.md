# Day 14 - 综合实战：完成一个真实后端功能

## 目标
将前 13 天的知识综合应用，完成一个完整的后端功能，从需求理解到测试部署。

## 项目选择

选择以下任务之一完成：

### 选项 A：新增一个完整的工具（推荐新手）
添加一个中等复杂度的工具，如 "Email Extractor" 或 "JSON Validator"。

### 选项 B：重构一个核心模块的错误处理
改进 `run_agent.py` 或 `model_tools.py` 中的错误处理，添加更多的 fallback 策略。

### 选项 C：优化一个性能瓶颈
如改进会话搜索的性能、加速工具分发、或优化 context 压缩。

### 选项 D：为一个平台添加适配器（高难度）
实现一个新的网关平台适配器（如 WeChat / Matrix / Mattermost）。

---

## 推荐路线：选项 A - 新增工具：JSON Validator

这个工具展现了完整的后端开发流程。

## 第 1 步：需求分析与设计（3 小时）

### 功能需求
```
工具名称：json_validator
输入参数：
  - json_string: 需要验证的 JSON 字符串
  - schema: 可选的 JSON Schema（用来验证结构）
输出：
  - 是否有效 (boolean)
  - 错误信息（如果无效）
  - 解析后的对象（如果有效）
  - Schema 验证结果（如果提供了 schema）
```

### 架构设计
```
┌─ tools/json_validator.py（实现）
├─ toolsets.py（注册 toolset）
├─ tests/tools/test_json_validator.py（测试）
└─ docs/（文档）
```

### 风险评估
```
- 依赖：需要 jsonschema 库（需在 requirements.txt 中）
- 权限：无特殊权限需求（纯本地处理）
- 安全性：有效防止 DoS（限制输入大小）
- 兼容性：支持 Python 3.10+
```

## 第 2 步：实现工具（4 小时）

### 2.1 创建工具文件
```python
# tools/json_validator.py

import json
import logging
from typing import Optional, Dict, Any
from jsonschema import validate, ValidationError, Draft7Validator

logger = logging.getLogger(__name__)

def validate_json(
    json_string: str,
    schema: Optional[str] = None,
    max_size: int = 1_000_000,  # 1 MB
    task_id: str = None
) -> str:
    """
    Validate JSON string and optionally against a JSON Schema.
    
    Returns:
        JSON object with keys: is_valid, parsed_object, errors
    """
    
    result = {
        "is_valid": False,
        "parsed_object": None,
        "errors": [],
        "schema_valid": None  # 如果提供了 schema
    }
    
    # 第 1 步：检查大小
    if len(json_string) > max_size:
        result["errors"].append(f"Input exceeds max size ({max_size} bytes)")
        return json.dumps(result)
    
    # 第 2 步：尝试解析 JSON
    try:
        parsed = json.loads(json_string)
        result["parsed_object"] = parsed
        result["is_valid"] = True
    except json.JSONDecodeError as e:
        result["errors"].append(f"JSON decode error: {e.msg} at line {e.lineno}")
        return json.dumps(result)
    
    # 第 3 步：如果提供了 schema，验证结构
    if schema:
        try:
            schema_obj = json.loads(schema)
            validate(instance=parsed, schema=schema_obj)
            result["schema_valid"] = True
        except json.JSONDecodeError:
            result["errors"].append(f"Invalid JSON Schema: {schema}")
        except ValidationError as e:
            result["schema_valid"] = False
            result["errors"].append(f"Schema validation failed: {e.message}")
    
    return json.dumps(result)

# 注册工具
from tools.registry import registry

registry.register(
    name="json_validator",
    toolset="data_tools",
    schema={
        "name": "json_validator",
        "description": "Validate JSON strings and optionally check against JSON Schema",
        "parameters": {
            "type": "object",
            "properties": {
                "json_string": {
                    "type": "string",
                    "description": "The JSON string to validate"
                },
                "schema": {
                    "type": "string",
                    "description": "Optional JSON Schema (as a string) to validate against"
                }
            },
            "required": ["json_string"]
        }
    },
    handler=lambda args, **kw: validate_json(
        json_string=args.get("json_string", ""),
        schema=args.get("schema"),
        task_id=kw.get("task_id")
    ),
    check_fn=lambda: True,  # 总是可用（无外部依赖）
    description="Validate and parse JSON with optional schema checking"
)
```

### 2.2 更新 toolsets.py
```python
# toolsets.py

TOOLSET_DEFINITIONS = {
    # ... 现有定义
    
    "data_tools": {
        "description": "Tools for data validation and transformation",
        "tools": ["json_validator", "csv_parser"],  # 可以后续添加更多
        "optional_dependencies": ["jsonschema"]
    }
}
```

### 2.3 添加依赖
```
# requirements.txt 中新增
jsonschema>=4.18.0
```

## 第 3 步：编写完整的测试套件（5 小时）

### 3.1 单元测试
```python
# tests/tools/test_json_validator.py

import pytest
import json
from tools.registry import registry
from model_tools import handle_function_call, get_tool_definitions

class TestJsonValidator:
    """JSON Validator 工具的测试套件"""
    
    def test_tool_registered(self):
        """验证工具被注册"""
        entry = registry.get_entry("json_validator")
        assert entry is not None
        assert entry.toolset == "data_tools"
    
    def test_valid_json(self):
        """验证有效的 JSON"""
        valid_json = '{"key": "value", "number": 42}'
        result = handle_function_call("json_validator", {"json_string": valid_json})
        result_dict = json.loads(result)
        
        assert result_dict["is_valid"] == True
        assert result_dict["parsed_object"]["key"] == "value"
        assert len(result_dict["errors"]) == 0
    
    def test_invalid_json(self):
        """验证无效的 JSON"""
        invalid_json = '{"unclosed": "string'
        result = handle_function_call("json_validator", {"json_string": invalid_json})
        result_dict = json.loads(result)
        
        assert result_dict["is_valid"] == False
        assert len(result_dict["errors"]) > 0
        assert "JSON decode error" in result_dict["errors"][0]
    
    def test_schema_validation_success(self):
        """验证通过 Schema 检查"""
        json_data = '{"name": "Alice", "age": 30}'
        schema = '''{
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name", "age"]
        }'''
        
        result = handle_function_call(
            "json_validator",
            {"json_string": json_data, "schema": schema}
        )
        result_dict = json.loads(result)
        
        assert result_dict["is_valid"] == True
        assert result_dict["schema_valid"] == True
    
    def test_schema_validation_failure(self):
        """验证未通过 Schema 检查"""
        json_data = '{"name": "Bob"}'  # 缺少 age
        schema = '''{
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name", "age"]
        }'''
        
        result = handle_function_call(
            "json_validator",
            {"json_string": json_data, "schema": schema}
        )
        result_dict = json.loads(result)
        
        assert result_dict["is_valid"] == True  # JSON 本身有效
        assert result_dict["schema_valid"] == False  # 但不符合 schema
    
    def test_size_limit(self):
        """验证大小限制"""
        # 创建一个超大 JSON 字符串
        large_json = '{"data": "' + "x" * 2_000_000 + '"}'
        
        result = handle_function_call(
            "json_validator",
            {"json_string": large_json}
        )
        result_dict = json.loads(result)
        
        assert result_dict["is_valid"] == False
        assert "exceeds max size" in result_dict["errors"][0]
    
    @pytest.mark.parametrize("json_str,expected_valid", [
        ('{}', True),
        ('[]', True),
        ('null', True),
        ('true', True),
        ('123', True),
        ('"string"', True),
        ('', False),
        ('{', False),
        ('undefined', False),
    ])
    def test_edge_cases(self, json_str, expected_valid):
        """边界情况测试"""
        result = handle_function_call(
            "json_validator",
            {"json_string": json_str}
        )
        result_dict = json.loads(result)
        assert result_dict["is_valid"] == expected_valid
    
    def test_tool_in_toolset(self):
        """验证工具在 toolset 中可用"""
        schemas = get_tool_definitions(
            enabled_toolsets=["data_tools"],
            quiet_mode=True
        )
        tool_names = [s["name"] for s in schemas]
        assert "json_validator" in tool_names
```

### 3.2 运行测试
```bash
# 运行你的新测试
scripts/run_tests.sh tests/tools/test_json_validator.py -v

# 运行完整测试确保无回归
scripts/run_tests.sh tests/ -q

# 检查覆盖率
scripts/run_tests.sh tests/tools/test_json_validator.py --cov=tools.json_validator
```

## 第 4 步：文档与集成（2 小时）

### 4.1 工具文档
```markdown
# JSON Validator Tool

## 功能
验证 JSON 字符串的语法，并可选择根据 JSON Schema 验证结构。

## 使用示例

### 基本验证
```
Input: {"json_string": "{\"name\": \"Alice\"}"}
Output: {
  "is_valid": true,
  "parsed_object": {"name": "Alice"},
  "errors": []
}
```

### Schema 验证
```
Input: {
  "json_string": "{\"age\": \"not a number\"}",
  "schema": "{\"type\": \"object\", \"properties\": {\"age\": {\"type\": \"number\"}}}"
}
Output: {
  "is_valid": true,
  "parsed_object": {"age": "not a number"},
  "schema_valid": false,
  "errors": ["Schema validation failed: 'not a number' is not of type 'number'"]
}
```

## 限制
- 最大输入大小：1 MB
- 无外部 API 依赖

## 常见用途
- API 响应验证
- 配置文件检查
- 数据清理
```

### 4.2 更新 AGENTS.md
在 AGENTS.md 的工具部分添加说明：
```
### 新增工具：json_validator

在 Day 14 实战项目中新增，用于 JSON 验证与 Schema 检查。
工具集：data_tools
依赖：jsonschema
```

## 第 5 步：验收与总结（1 小时）

### 5.1 验收清单
- [ ] 代码无语法错误
- [ ] 所有单元测试通过
- [ ] 无新增回归（full test suite 通过）
- [ ] 覆盖率 > 80%
- [ ] 工具在 CLI 中可用
- [ ] 工具在 Gateway 中可用
- [ ] 文档完整且准确
- [ ] 没有硬编码路径（Profile-safe）

### 5.2 交付物清单
创建 `notes/day14-capstone-report.md`：
```markdown
# Day 14 综合实战报告

## 项目选择
- [x] 选项 A：新增 JSON Validator 工具

## 需求分析
- 输入参数：json_string, schema（可选）
- 输出：是否有效、错误列表、解析结果、Schema 验证结果

## 实现统计
- 新增文件：2 个（tools/json_validator.py, tests/tools/test_json_validator.py）
- 修改文件：2 个（toolsets.py, requirements.txt）
- 代码行数：总计 ~400 行（含测试）

## 测试覆盖
- 单元测试：8 个
- 参数化测试：9 个场景
- 覆盖率：95%

## 学到的关键知识
1. 工具注册的完整流程
2. Schema 验证的集成
3. 错误处理与返回格式规范
4. Profile-safe 编码实践
5. 完整的测试-驱动开发

## 已知限制与未来改进
- 限制输入大小为 1 MB（可配置）
- 不支持自定义 JSON 编码（仅 UTF-8）
- 可以后续添加 CSV/YAML/XML 验证工具

## 验收结果
- [x] 代码审查通过
- [x] 所有测试通过
- [x] 无代码覆盖率下降
- [x] 文档完整
```

## 最终检查清单

在宣布完成前，自检：

```
[ ] 代码改动 < 500 行（含测试）
[ ] 每个文件有目的和意义
[ ] 没有重复代码
[ ] 异常处理完整
[ ] 没有 print()，都用 logger
[ ] 没有硬编码路径或密钥
[ ] 工具返回 JSON（不是其他格式）
[ ] 测试覆盖关键路径与边界情况
[ ] 文档有示例与限制说明
[ ] PR 字段填完整（what/why/how/testing）
```

## 宣布完成

当所有项都检查完毕后，你可以：
1. 创建一个 Feature Branch
2. 提交代码与完整的单元测试
3. 运行完整测试确认无回归
4. 提交 PR 与详细的变更说明
5. 等待 Review 与 Merge

---

## 14 天学习总结

通过 14 天的学习和实战，你应该已经：

### 知识维度
- ✅ 理解完整的 Agent 循环与工具调用机制
- ✅ 掌握工具注册、分发与执行的全流程
- ✅ 理解会话持久化与并发安全
- ✅ 学会 Prompt 构建与 Context 管理
- ✅ 理解多平台网关的设计与实现
- ✅ 掌握 Profile 隔离与配置治理
- ✅ 学会测试驱动开发与质量保证

### 能力维度
- ✅ 能独立新增一个完整的后端工具
- ✅ 能改进现有功能而不破坏架构
- ✅ 能诊断和修复 bug
- ✅ 能优化性能和成本
- ✅ 能遵循项目约束编写高质量代码

### 贡献准备
- ✅ 理解项目的设计理念与架构约束
- ✅ 遵循编码规范与最佳实践
- ✅ 能编写清晰的 commit message 与 PR 说明
- ✅ 能独立完成从需求到交付的全流程

祝贺！你已经准备好为 Hermes Agent 项目做出生产级贡献。🚀

