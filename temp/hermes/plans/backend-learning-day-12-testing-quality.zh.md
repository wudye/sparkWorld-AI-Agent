# Day 12 - 测试策略与质量保证

## 目标
掌握项目的测试框架、CI 一致性约束、以及如何编写可靠的测试来防止回归。

## 关键文件
- `tests/conftest.py`（测试配置与 fixture）
- `scripts/run_tests.sh`（CI wrapper）
- `tests/` 下的各个测试文件

## 学习内容

### 1) 测试隔离的三个层次
```python
# tests/conftest.py

@pytest.fixture(scope="session", autouse=True)
def _isolate_hermes_home(tmp_path_factory):
    """隔离级别 1：临时 HERMES_HOME"""
    tmp_home = tmp_path_factory.mktemp("hermes_home")
    os.environ["HERMES_HOME"] = str(tmp_home)
    yield
    # teardown

@pytest.fixture(autouse=True)
def _clean_environment():
    """隔离级别 2：清除所有 API 密钥"""
    api_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", ...]
    original_keys = {}
    
    for key in api_keys:
        if key in os.environ:
            original_keys[key] = os.environ.pop(key)
    
    yield
    
    # 恢复
    os.environ.update(original_keys)

@pytest.fixture(autouse=True)
def _set_ci_environment():
    """隔离级别 3：统一时区与语言"""
    os.environ["TZ"] = "UTC"
    os.environ["LANG"] = "C.UTF-8"
    yield
```

**隔离的好处**：
- 测试结果可复现（不依赖本地环境）
- 防止意外修改用户的真实配置
- 模拟 CI 环境的精确行为

### 2) scripts/run_tests.sh 的作用
```bash
#!/bin/bash
# scripts/run_tests.sh

# 第 1 步：设置隔离环境
export TZ=UTC
export LANG=C.UTF-8
unset OPENAI_API_KEY ANTHROPIC_API_KEY ...

# 第 2 步：运行 pytest 与固定的 xdist 并发度
python -m pytest tests/ -q -n 4 "$@"
# -n 4：固定 4 并发（与 CI ubuntu-latest 的 CPU 数量一致）
# -q：quiet 模式
# "$@"：传递所有其他参数

# 第 3 步：验证返回码
exit $?
```

**为什么不能直接 pytest？**

| 方面 | 直接 pytest | 使用 wrapper |
|------|-----------|-----------|
| 并发度 | `-n auto`（本机 CPU 数，通常 16+） | `-n 4`（CI 标准） |
| API 密钥 | 从环境读取 | 全部清除 |
| 时区 | 本地时区 | UTC |
| 语言 | 系统语言 | C.UTF-8 |
| 结果 | 本机通过，CI 失败 | 本机 CI 一致 |

### 3) 常见的测试 fixture
```python
# tests/conftest.py 中的实用 fixture

@pytest.fixture
def hermes_home_temp(tmp_path):
    """返回临时 HERMES_HOME 路径"""
    return tmp_path / ".hermes"

@pytest.fixture
def mock_session_db(hermes_home_temp):
    """创建一个测试用 SessionDB"""
    from hermes_state import SessionDB
    db = SessionDB(db_path=hermes_home_temp / "state.db")
    yield db
    db.close()

@pytest.fixture
def mock_ai_agent():
    """创建一个测试用 AIAgent（禁用网络）"""
    from run_agent import AIAgent
    
    agent = AIAgent(
        model="claude-3-5-sonnet",
        max_iterations=5,
        enabled_toolsets=["dummy"],  # 只启用本地工具
        quiet_mode=True
    )
    yield agent

@pytest.fixture
def monkeypatch_openai():
    """Mock OpenAI API 调用"""
    def mock_create(*args, **kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(
                    content="Mock response",
                    tool_calls=[]
                )
            )]
        )
    
    with patch("openai.OpenAI.chat.completions.create", mock_create):
        yield
```

### 4) 典型的测试结构
```python
# tests/test_approval.py

def test_detect_dangerous_command():
    """测试危险命令检测"""
    # Arrange（准备数据）
    command = "rm -rf /"
    
    # Act（执行操作）
    is_dangerous, pattern_key, desc = detect_dangerous_command(command)
    
    # Assert（验证结果）
    assert is_dangerous == True
    assert "delete" in pattern_key.lower()

def test_approval_whitelist():
    """测试审批白名单"""
    # Arrange
    session_key = "test_session"
    command = "rm -rf /etc"
    
    # Act
    add_to_allowlist("delete in root", session_key)
    result = request_approval_sync(command, session_key)
    
    # Assert
    assert result == "session"  # 已在白名单中

@pytest.mark.parametrize("command,expected_dangerous", [
    ("rm -rf /", True),
    ("rm -rf ./data", True),
    ("rm ./file.txt", False),
    ("ls -la", False),
])
def test_dangerous_patterns(command, expected_dangerous):
    """参数化测试多个命令"""
    is_dangerous, _, _ = detect_dangerous_command(command)
    assert is_dangerous == expected_dangerous
```

## 实践任务

### 任务 1: 理解 CI 一致性检查
1. 运行项目的测试两种方式：
```bash
# 方式 A：直接 pytest（可能失败或不一致）
python -m pytest tests/tools/test_approval.py -v

# 方式 B：用 wrapper（保证一致）
scripts/run_tests.sh tests/tools/test_approval.py -v
```

2. 记录差异（如果有）：
   - 并发度变化导致的时序问题
   - API 密钥导致的条件跳过
   - 时区导致的时间比较错误

**输出**：对比报告（两种方式的运行结果）

### 任务 2: 为你的改动编写 3 个单元测试
选择你在前面 Day 中做过的改动（如 Day 03 的 dummy 工具）：

```python
# tests/test_my_changes.py

import pytest
from tools.registry import registry
from model_tools import handle_function_call, get_tool_definitions
import json

class TestDummyTool:
    """Dummy tool 的测试套件"""
    
    def test_dummy_tool_registered(self):
        """验证 dummy 工具被正确注册"""
        entry = registry.get_entry("dummy_add")
        assert entry is not None
        assert entry.toolset == "dummy"
    
    def test_dummy_tool_execution(self):
        """验证 dummy 工具的执行结果"""
        result = handle_function_call("dummy_add", {"a": 3, "b": 5})
        result_dict = json.loads(result)
        assert result_dict["result"] == 8
    
    def test_dummy_tool_unavailable_when_disabled(self):
        """验证禁用 toolset 时工具不可用"""
        schemas = get_tool_definitions(
            enabled_toolsets=["web_tools"],  # 不包括 "dummy"
            quiet_mode=True
        )
        tool_names = [s["name"] for s in schemas]
        assert "dummy_add" not in tool_names

@pytest.mark.parametrize("a,b,expected", [
    (0, 0, 0),
    (1, 1, 2),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_dummy_add_edge_cases(a, b, expected):
    """边界值测试"""
    result = handle_function_call("dummy_add", {"a": a, "b": b})
    result_dict = json.loads(result)
    assert result_dict["result"] == expected
```

**验收**：`scripts/run_tests.sh tests/test_my_changes.py -v` 通过全部 3 个测试。

### 任务 3: 添加一个集成测试
```python
# tests/test_integration_e2e.py

def test_complete_agent_flow(mock_ai_agent, mock_session_db):
    """端到端测试：完整的 Agent 流程"""
    
    # 1. 创建会话
    session_key = "test_e2e"
    mock_session_db.create_session(session_key, "cli", "test-model")
    
    # 2. 模拟用户消息
    user_message = "What is 2 + 2?"
    
    # 3. 运行 Agent（这会调用模型，需要 mock）
    with patch("openai.OpenAI.chat.completions.create") as mock_llm:
        mock_llm.return_value = SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(
                    content="The answer is 4",
                    tool_calls=[]
                )
            )]
        )
        
        response = mock_ai_agent.chat(user_message)
    
    # 4. 验证结果
    assert "4" in response
    
    # 5. 验证持久化
    messages = mock_session_db.get_session_messages(session_key)
    # 应该有至少一条消息被保存
```

**验收**：集成测试通过。

### 任务 4: 覆盖率分析与改进
```bash
# 生成覆盖率报告
scripts/run_tests.sh --cov=tools --cov-report=html

# 打开 htmlcov/index.html 查看覆盖率
# 找到未覆盖的代码行，为它们编写测试

# 目标：至少 80% 的覆盖率
```

## 风险点与注意事项

⚠️ **本地通过，CI 失败**：最常见原因是没用 wrapper 脚本。
⚠️ **Flaky 测试**：测试结果随机失败，通常由于时序问题或 mock 不完整。
⚠️ **过度 mock**：Mock 太多导致测试没有真实性，不能发现 bug。
⚠️ **测试数据污染**：一个测试修改全局状态，导致下一个测试失败。

## 交付物

创建 `notes/day12-testing.md`：
- 测试隔离的三个层次说明
- CI wrapper 脚本的作用
- 常用 fixture 的清单
- 任务 1-4 的代码与验证截图
- 覆盖率分析结果

## 验收标准

你能够：
1. ✅ 理解为什么不能直接 pytest
2. ✅ 用 wrapper 脚本运行完整测试套件
3. ✅ 为新功能编写 3 个单元测试
4. ✅ 实现一个集成测试
5. ✅ 分析并改进代码覆盖率

**最后检查**：能否在本地复现 CI 的测试环境？

