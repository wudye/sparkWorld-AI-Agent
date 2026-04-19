# Day 06 - 危险命令检测与审批机制

## 目标
理解危险命令识别的正则模式、审批流的同步/异步差异、以及如何安全地扩展防护规则。这涉及核心安全问题。

## 关键文件
- `tools/approval.py`
- `tools/terminal_tool.py`（集成点）
- `tests/tools/test_approval.py`（参考测试）

## 学习内容

### 1) 危险模式识别的归一化
```python
def _normalize_command_for_detection(command: str) -> str:
    """清理命令以进行模式匹配"""
    # 1. 去掉 ANSI 逃逸码（\033[...m）
    command = strip_ansi(command)
    
    # 2. 去掉 null 字符
    command = command.replace('\x00', '')
    
    # 3. Unicode 归一化（fullwidth → halfwidth）
    command = unicodedata.normalize('NFKC', command)
    
    # 4. 转小写
    command = command.lower()
    
    return command
```

**为什么这么复杂？** 攻击者可能用 ANSI 码、Unicode 变体来绕过简单的正则检测。

### 2) 核心危险模式分类
```python
DANGEROUS_PATTERNS = [
    # 文件删除
    (r'\brm\s+(-[^\s]*\s+)*/', "delete in root path"),
    (r'\brm\s+-[^\s]*r', "recursive delete"),
    
    # 权限修改
    (r'\bchmod\s+.*?(777|666|o\+w)\b', "world-writable permissions"),
    
    # 数据库破坏
    (r'\bDROP\s+(TABLE|DATABASE)\b', "SQL DROP"),
    (r'\bDELETE\s+FROM\b(?!.*\bWHERE\b)', "SQL DELETE without WHERE"),
    
    # 远程代码执行
    (r'\b(curl|wget)\b.*\|\s*sh\b', "pipe remote to shell"),
    
    # 进程自杀（对 Gateway 特别危险）
    (r'\bhermes\s+gateway\s+(stop|restart)\b', "stop/restart hermes gateway"),
    (r'\b(pkill|killall)\b.*hermes\b', "kill hermes process"),
    
    # ... 还有 30+ 个模式
]
```

**关键特性**：
- 每个模式对应一个人类可读的描述
- 正则按优先级排序（最危险的优先）
- 支持多种混淆形式（如 `git\s+reset\s+--hard`）

### 3) CLI vs Gateway 审批流的差异

**CLI 模式（同步）：**
```python
# tools/approval.py
def request_approval_sync(command: str, session_key: str):
    """同步阻塞，直到用户回复"""
    
    # 1. 检测危险性
    is_dangerous, pattern_key, desc = detect_dangerous_command(command)
    if not is_dangerous:
        return "once"  # 非危险，直接批准
    
    # 2. 检查永久 allowlist
    if is_in_allowlist(pattern_key, session_key):
        return "session"  # 已批准过，直接通过
    
    # 3. 交互式提示（阻塞等待用户输入）
    print(f"⚠️  Dangerous command detected: {desc}")
    print(f"Command: {command}")
    response = input("Approve? (once/session/always/deny) > ")
    
    if response == "always":
        add_to_permanent_allowlist(pattern_key, session_key)
    
    return response
```

**Gateway 模式（异步）：**
```python
# 无法直接 input()，需要通过事件系统

# 1. 检测危险性
is_dangerous, pattern_key, desc = detect_dangerous_command(command)

# 2. 创建待审批条目
entry = _ApprovalEntry(data={
    "command": command,
    "description": desc,
    "pattern_keys": [pattern_key]
})

# 3. 加入会话的审批队列
_gateway_queues[session_key].append(entry)

# 4. 通知 RPC 前端用户
notify_cb = _gateway_notify_cbs[session_key]
notify_cb({"command": command, "description": desc})

# 5. 阻塞等待事件（用户会通过 /approve 命令回复）
result = entry.event.wait(timeout=300)

# 6. 继续执行或拒绝
if result == "deny":
    raise ApprovalDenied()
```

**关键区别**：
- CLI: input() 同步阻塞
- Gateway: 用 threading.Event 和 RPC 异步通知

### 4) 审批决策的四种结果
```python
# 1. "once" - 仅此一次通过
# 2. "session" - 本会话内此类命令都通过
# 3. "always" - 永久允许（保存到 config.yaml）
# 4. "deny" - 拒绝（抛异常）
```

## 实践任务

### 任务 1: 危险模式的覆盖分析
1. 打开 `DANGEROUS_PATTERNS` 列表
2. 分类所有模式（30+ 个）：
   - 文件操作（rm / chmod / chown）
   - SQL 操作（DROP / DELETE / TRUNCATE）
   - 远程执行（curl/wget | sh）
   - 进程控制（kill / pkill）
   - Gateway 自杀（hermes gateway stop）
   - 其他
3. 对每个模式写一个正样本和负样本

**输出**：Markdown 表格
```
| 类型 | 模式 | 描述 | 正样本 | 负样本 |
|------|------|------|--------|--------|
| 删除 | `rm -rf /` | 根目录删除 | `rm -rf /tmp` | `rm -rf ./tmp` |
| ... |
```

### 任务 2: 新增一个危险模式
假设要防止 `git rebase` 在 shared branch 上执行（常见事故）。

1. 设计正则：
```python
# ❌ 危险：在 main 或 master 分支上 rebase
git rebase origin/main
git rebase --interactive main

# ✅ 安全：在 feature 分支上 rebase
git rebase feature-branch
```

2. 实现模式：
```python
(r'\bgit\s+rebase\b.*\b(main|master|develop)\b', "rebase on protected branch"),
```

3. 写测试：
```python
def test_git_rebase_protection():
    dangerous, key, desc = detect_dangerous_command("git rebase origin/main")
    assert dangerous == True
    
    dangerous, key, desc = detect_dangerous_command("git rebase feature-xyz")
    assert dangerous == False
```

4. 添加到 `DANGEROUS_PATTERNS` 列表，运行 `scripts/run_tests.sh tests/tools/test_approval.py` 验证。

### 任务 3: 审批流程的集成测试
```python
def test_approval_flow_cli():
    """模拟 CLI 审批流程"""
    from tools.approval import request_approval_sync
    
    # Mock input 函数
    with patch('builtins.input', return_value='once'):
        result = request_approval_sync("rm -rf /etc", session_key="test")
        assert result == "once"
    
    # 测试 allowlist
    with patch('builtins.input', return_value='always'):
        result = request_approval_sync("rm -rf /etc", session_key="test")
        assert result == "always"
    
    # 再次调用应该直接通过
    result = request_approval_sync("rm -rf /etc", session_key="test")
    assert result == "session"  # 已在会话 allowlist 中

def test_approval_flow_gateway():
    """模拟 Gateway 异步审批"""
    from tools.approval import register_gateway_notify
    
    approvals_sent = []
    def mock_notify(data):
        approvals_sent.append(data)
    
    session_key = "gw_session_001"
    register_gateway_notify(session_key, mock_notify)
    
    # 触发危险命令检测
    entry = _ApprovalEntry({...})
    # 验证通知被发送
    assert len(approvals_sent) == 1
```

### 任务 4: 模式规则的性能分析
现有 30+ 个模式，每个命令都要逐个测试。
1. 测试对一个危险命令的检测时间
2. 建议优化方案（如：编译一个大的 OR 正则）
3. 衡量编译时间 vs 检测时间的权衡

## 风险点与注意事项

⚠️ **正则的误伤**：如果模式太宽松，会误判合法命令。例如 `grep -r` 会被认为"递归"。
⚠️ **新模式的回归**：添加新模式时要充分测试负样本，避免误杀。
⚠️ **Gateway 中的竞态**：多个 agent 同时提交危险命令，approval queue 的顺序要明确。
⚠️ **Allowlist 的持久化**：永久 allowlist 存到 config.yaml，不要丢失。

## 交付物

创建 `notes/day06-approval.md`：
- 危险模式分类与完整列表
- CLI vs Gateway 审批流的对比图
- 任务 2 的新模式代码 + 测试
- 任务 3 的集成测试代码
- 性能分析与优化建议

## 验收标准

你能够：
1. ✅ 说出 30+ 个危险模式的分类
2. ✅ 设计并实现一个新的危险模式（含测试）
3. ✅ 解释 CLI 与 Gateway 审批的异步差异
4. ✅ 实现一个审批流的单元测试
5. ✅ 识别并修复一个审批规则的误伤

**最后检查**：能否添加 5 个新模式而不造成回归？

