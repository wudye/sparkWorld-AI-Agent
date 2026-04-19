# Sandbox 深度解析：本地执行 vs Docker隔离

> 本文档详细解答"Sandbox如何工作"以及"Agent执行Shell命令的隔离机制"

---

## 一、Sandbox的核心概念

### 问题：什么是Sandbox？

**简单定义**：Sandbox是一个**隔离的执行环境**，Agent在其中运行命令、读写文件，但无法访问系统的其他部分。

**核心特性**：
1. **文件隔离** - Agent只能访问分配给它的目录
2. **进程隔离** - Agent的进程不能影响其他用户的进程
3. **虚拟路径** - Agent看到的路径与实际路径不同
4. **权限限制** - Agent无法执行危险操作

---

## 二、Sandbox的两种实现方式

### 2.1 LocalSandbox（本地文件系统）

#### 工作原理

```
Agent中的代码：
  read_file('/mnt/user-data/workspace/file.txt')

转换为实际操作：
  read_file('/real/path/thread_123/workspace/file.txt')
```

**虚拟路径到物理路径的映射**：

```python
# 虚拟路径 (Agent看到的)
/mnt/user-data/workspace/    ← 工作目录
/mnt/user-data/uploads/      ← 上传文件
/mnt/user-data/outputs/      ← 输出文件
/mnt/skills/                 ← 技能目录 (只读)

# 物理路径 (真实存储位置)
/var/deerflow/threads/thread_123/workspace/
/var/deerflow/threads/thread_123/uploads/
/var/deerflow/threads/thread_123/outputs/
/opt/deerflow/skills/public/
```

#### 隔离机制

```
用户A的Agent              用户B的Agent
    ↓                          ↓
LocalSandbox('user_a')   LocalSandbox('user_b')
    ↓                          ↓
虚拟路径:                  虚拟路径:
/mnt/user-data/          /mnt/user-data/
    ↓                          ↓
物理路径:                  物理路径:
/thread_a/               /thread_b/
    ↓                          ↓
真实文件系统
(文件系统权限控制隔离)
```

#### 关键限制

**LocalSandbox禁用了bash工具**：

```python
# tools.py
DEFAULT_BASH_ENABLED = False

# 为什么？
# 直接执行bash命令太危险：
# rm -rf /              # 删除整个系统
# dd if=/dev/zero      # 填充磁盘
# fork(); fork(); ...  # Fork炸弹
```

如果需要bash执行，**必须使用AioSandbox（Docker隔离）**。

---

### 2.2 AioSandbox（Docker容器隔离）

#### 工作原理

```
Agent请求执行命令
    ↓
通过Docker API启动容器
    ↓
在容器内执行命令
    ↓
获取输出，销毁容器
```

**具体流程**：

```python
# 主进程中
class AioSandbox(Sandbox):
    async def execute_command(self, command: str) -> str:
        # 1. 连接Docker daemon
        client = docker.from_env()
        
        # 2. 创建容器，挂载虚拟路径到真实目录
        container = client.containers.run(
            image='python:3.12',
            command=['bash', '-c', command],
            volumes={
                '/real/path/thread_123/workspace': {
                    'bind': '/mnt/user-data/workspace',
                    'mode': 'rw'
                },
                '/opt/deerflow/skills': {
                    'bind': '/mnt/skills',
                    'mode': 'ro'
                }
            },
            working_dir='/mnt/user-data/workspace',
            detach=False,
            remove=True
        )
        
        # 3. 等待容器执行完毕
        result = container.wait()
        
        # 4. 返回输出
        logs = container.logs().decode()
        return logs
```

#### 隔离特性

```
每个命令执行流程：

Time T=0:     创建Docker容器
              ├─ 完全独立的文件系统
              ├─ 独立的进程树
              ├─ 独立的网络(可选)
              └─ 挂载虚拟路径

Time T=1:     执行Agent的命令
              ├─ 命令在容器内运行
              ├─ 不能访问主机文件系统
              ├─ 不能影响主机进程
              └─ 可以执行任何命令（即使是rm -rf /）

Time T=2:     命令执行完成
              └─ 收集输出

Time T=3:     销毁容器
              ├─ 所有修改都被销毁
              ├─ 主机文件系统不受影响
              └─ 占用的资源被释放
```

#### Docker隔离的安全保证

```
即使Agent执行恶意命令：

# 容器内命令
rm -rf /

结果：
✓ 删除的是容器内的文件系统
✓ 主机的/保持完整
✓ 其他用户的数据不受影响
✓ 容器销毁后痕迹消失

宿主机上看起来：
# 容器启动前
$ ls /thread_123/workspace
file1.txt

# 容器执行 rm -rf /
# 容器内文件被删除

# 容器停止
$ ls /thread_123/workspace
file1.txt   # 主机上的原始文件完好！

为什么？因为容器有独立的root文件系统
```

---

## 三、LocalSandbox vs AioSandbox对比

| 特性 | LocalSandbox | AioSandbox |
|---|---|---|
| **隔离强度** | 文件系统权限 | 容器隔离 |
| **性能** | ⚡️ 快（无开销） | 🐢 慢（容器启动） |
| **bash支持** | ❌ 禁用 | ✅ 启用 |
| **适用场景** | 开发、简单任务 | 生产、不信任代码 |
| **资源占用** | 低 | 高 |
| **启动时间** | <1ms | 500ms-2s |
| **依赖** | 无 | Docker |
| **多用户安全** | ⚠️ 中等 | ✅ 高 |
| **进程隔离** | ❌ 否 | ✅ 是 |

---

## 四、虚拟路径映射详解

### 4.1 为什么需要虚拟路径？

**问题1**：如果Agent知道真实路径，可能访问其他用户的目录

```
坏的设计：
User A的Agent → /var/deerflow/threads/thread_a/
User B可以猜到：/var/deerflow/threads/thread_b/
→ User A的Agent可能读到User B的数据！
```

**问题2**：真实路径暴露系统架构信息

```
如果Agent看到路径 /var/lib/mysql/
就知道系统使用MySQL，可能针对性攻击
```

**虚拟路径的解决方案**：

```
Agent永远只看到：
/mnt/user-data/workspace/
/mnt/user-data/uploads/
/mnt/user-data/outputs/
/mnt/skills/

不管真实存储在哪里（可以是NFS、S3、另一个机器）
Agent无法推断系统架构
```

### 4.2 路径映射的实现

```python
class LocalSandbox(Sandbox):
    def __init__(self, thread_id: str, base_path: str):
        self.thread_id = thread_id
        self.base_path = base_path  # /var/deerflow/threads/
        
    def resolve_path(self, virtual_path: str) -> str:
        """将虚拟路径转换为物理路径"""
        
        # 虚拟路径示例
        # /mnt/user-data/workspace/file.txt
        
        if virtual_path.startswith('/mnt/user-data'):
            # 提取相对部分
            relative = virtual_path[len('/mnt/user-data'):]  # /workspace/file.txt
            
            # 映射到物理路径
            physical = os.path.join(
                self.base_path,
                self.thread_id,
                relative
            )
            # 结果：/var/deerflow/threads/thread_123/workspace/file.txt
            
        elif virtual_path.startswith('/mnt/skills'):
            relative = virtual_path[len('/mnt/skills'):]
            physical = os.path.join('/opt/deerflow/skills', relative)
        
        else:
            raise SecurityError(f"Invalid path: {virtual_path}")
        
        # 安全检查：防止目录穿越攻击
        physical = os.path.abspath(physical)
        
        if not physical.startswith(self.base_path) and \
           not physical.startswith('/opt/deerflow/skills'):
            raise SecurityError(f"Path traversal detected: {virtual_path}")
        
        return physical
```

### 4.3 目录穿越攻击防护

```
攻击尝试1：
virtual_path = "/mnt/user-data/../../../../etc/passwd"

resolve_path()会：
1. 拼接：/var/deerflow/threads/thread_123/../../../../etc/passwd
2. 规范化：/etc/passwd
3. 安全检查失败！
4. 抛出SecurityError ✓

攻击尝试2：
virtual_path = "/mnt/user-data/../../../etc/passwd"

同样被拦截 ✓
```

---

## 五、Agent执行Shell命令的实际流程

### 5.1 使用LocalSandbox的场景（开发环境）

```
场景：开发环境，执行简单任务

User: "列出workspace目录"

↓

Agent代码：
  sandbox.list_dir('/mnt/user-data/workspace')

↓

LocalSandbox.list_dir()：
  1. 虚拟路径 → 物理路径转换
     /mnt/user-data/workspace →
     /var/deerflow/threads/thread_123/workspace
  
  2. 执行Python os.listdir()
     files = os.listdir('/var/deerflow/threads/thread_123/workspace')
  
  3. 返回文件列表
     ['file1.txt', 'script.py', 'data.csv']

↓

Agent得到结果，继续推理
```

**限制**：
- 不支持bash工具
- Agent无法执行复杂shell命令
- 只能读写文件、列出目录、搜索文件

### 5.2 使用AioSandbox的场景（生产环境）

```
场景：生产环境，执行shell命令

User: "运行Python脚本分析数据"

↓

Agent代码（仍然用同样的接口）：
  result = sandbox.execute_command('python analysis.py data.csv')

↓

AioSandbox.execute_command()：
  
  1. 连接Docker
     client = docker.from_env()
  
  2. 创建容器
     container = client.containers.run(
         image='python:3.12',
         command=['bash', '-c', 'python analysis.py data.csv'],
         volumes={
             '/var/deerflow/threads/thread_123/workspace':
             {
                 'bind': '/mnt/user-data/workspace',
                 'mode': 'rw'
             }
         }
     )
  
  3. 等待完成
     container.wait()
  
  4. 收集输出
     output = container.logs()
  
  5. 销毁容器
     container.remove()

↓

Agent得到输出结果
```

**优势**：
- 完全隔离的Shell环境
- 支持任何bash命令
- 多用户并发安全
- 恶意命令无法影响主机

---

## 六、虚拟路径在Docker中的工作原理

### 6.1 Docker Volume挂载

```
主机文件系统                容器文件系统

/var/deerflow/
└─ threads/
   └─ thread_123/
      ├─ workspace/  ──────→ /mnt/user-data/workspace/
      ├─ uploads/    ──────→ /mnt/user-data/uploads/
      └─ outputs/    ──────→ /mnt/user-data/outputs/

/opt/deerflow/
└─ skills/ ────────────────→ /mnt/skills/ (只读)
```

**具体Docker命令**：

```bash
docker run \
  --rm \
  --volume /var/deerflow/threads/thread_123/workspace:/mnt/user-data/workspace:rw \
  --volume /var/deerflow/threads/thread_123/uploads:/mnt/user-data/uploads:rw \
  --volume /var/deerflow/threads/thread_123/outputs:/mnt/user-data/outputs:rw \
  --volume /opt/deerflow/skills:/mnt/skills:ro \
  --working-dir /mnt/user-data/workspace \
  python:3.12 \
  bash -c "python analysis.py"
```

### 6.2 容器内的虚拟路径执行

```
容器启动后，Agent在容器内执行：

bash: /mnt/user-data/workspace $ ls
data.csv  file1.txt  script.py

bash: /mnt/user-data/workspace $ cat data.csv
...

实际上读的是主机上的：
/var/deerflow/threads/thread_123/workspace/data.csv

但是：
- 容器进程无法访问主机的其他部分
- 如果容器进程崩溃（例如OOM），主机不受影响
- 容器销毁后，修改会被保留在主机（因为使用了volume）
```

---

## 七、多用户隔离的完整流程

### 场景：同一时刻，User A和User B都在使用系统

```
┌─────────────────────────────────────────────┐
│          DeerFlow后端系统                     │
├─────────────────────────────────────────────┤
│                                              │
│  User A请求          User B请求              │
│      ↓                    ↓                  │
│  Agent执行           Agent执行               │
│  (thread_a)          (thread_b)              │
│      ↓                    ↓                  │
│  Sandbox             Sandbox                │
│  thread_id='a'       thread_id='b'           │
│      ↓                    ↓                  │
│  虚拟路径:           虚拟路径:                │
│  /mnt/user-data/    /mnt/user-data/        │
│      ↓                    ↓                  │
│  物理路径:           物理路径:                │
│  /threads/a/         /threads/b/            │
│      ↓                    ↓                  │
│  文件系统隔离（操作系统权限）                 │
│                                              │
└─────────────────────────────────────────────┘
```

**隔离保证**：

1. **文件隔离**
   ```
   User A访问 /mnt/user-data/workspace/file.txt
   实际访问 /threads/a/workspace/file.txt
   
   User B访问 /mnt/user-data/workspace/file.txt
   实际访问 /threads/b/workspace/file.txt
   
   两个不同的物理文件，不会相互污染
   ```

2. **进程隔离**（仅Docker）
   ```
   User A的bash进程在容器 docker_a 内
   User B的bash进程在容器 docker_b 内
   
   即使User A的进程crash
   User B的容器继续运行
   ```

3. **资源隔离**（仅Docker）
   ```
   User A的bash运行过程中内存溢出
   容器 docker_a 被OOM杀死
   主机继续运行
   User B不受影响
   ```

---

## 八、安全考虑和限制

### 8.1 LocalSandbox的安全问题

```python
# ❌ 潜在问题1：恶意文件写入
sandbox.write_file('/mnt/user-data/workspace/malware.sh', '...恶意代码...')
# 后续可能被其他进程执行

# ✓ 缓解：系统不会自动执行用户目录中的脚本

# ❌ 潜在问题2：资源耗尽
for i in range(1000000):
    sandbox.write_file(f'/mnt/user-data/workspace/file_{i}', 'x' * 1000000)
# 磁盘满，影响系统

# ✓ 缓解：设置disk quota，限制每个thread的使用量

# ❌ 潜在问题3：无法隔离进程
# LocalSandbox中没有bash工具，所以这个问题不存在
```

### 8.2 AioSandbox的安全性

```python
# ✓ 优势1：完全的进程隔离
container.run('rm -rf /')  # 只删除容器内的文件
# 主机的 / 保持完整

# ✓ 优势2：资源隔离
container.run(
    'yes > /dev/null',  # 无限循环
    mem_limit='512m'    # 内存限制
)
# 最多使用512MB内存，超出则被杀死

# ✓ 优势3：网络隔离
# 可以禁用网络，防止恶意连接外部

# ⚠️ 缺陷：性能开销
# 每次启动容器需要500ms-2s
# 频繁的小任务会很慢

# ⚠️ 缺陷：资源占用
# 每个容器占用一些内存和磁盘
# 不能无限扩展
```

---

## 九、实际场景示例

### 场景1：用户上传CSV文件，Agent分析

```
步骤1：文件上传
└─ POST /api/threads/abc/uploads
   └─ 文件保存到 /threads/abc/uploads/data.csv

步骤2：Agent启动
└─ LangGraph调用Agent
   └─ 中间件链：UploadsMiddleware注入文件信息

步骤3：Agent读取文件
└─ Agent代码：
   content = sandbox.read_file('/mnt/user-data/uploads/data.csv')
   
└─ LocalSandbox.read_file():
   physical_path = '/threads/abc/uploads/data.csv'
   with open(physical_path) as f:
       return f.read()

步骤4：Agent处理并生成报告
└─ Agent代码：
   result = sandbox.write_file(
       '/mnt/user-data/outputs/report.txt',
       'Analysis: ...'
   )
   
└─ LocalSandbox.write_file():
   physical_path = '/threads/abc/outputs/report.txt'
   with open(physical_path, 'w') as f:
       f.write(content)

步骤5：用户下载报告
└─ GET /api/threads/abc/artifacts/report.txt
   └─ 读取 /threads/abc/outputs/report.txt
   └─ 返回给用户
```

### 场景2：Agent执行复杂Python分析任务

```
使用AioSandbox（生产环境）

步骤1：Agent调用bash
└─ result = sandbox.execute_command('python analyze.py --input data.csv')

步骤2：AioSandbox启动Docker容器
└─ docker run \
     --volume /threads/abc/workspace:/mnt/user-data/workspace:rw \
     python:3.12 \
     bash -c 'python analyze.py --input data.csv'

步骤3：容器内执行脚本
└─ 脚本读取 /mnt/user-data/workspace/data.csv
   └─ 实际是主机上的 /threads/abc/workspace/data.csv
   
└─ 脚本生成 /mnt/user-data/outputs/results.json
   └─ 实际是主机上的 /threads/abc/outputs/results.json

步骤4：容器完成，返回输出
└─ output = container.logs()

步骤5：容器销毁
└─ container.remove()
   └─ 临时文件清理，但输出文件保留在主机

步骤6：Agent继续处理结果
└─ results = json.loads(output)
```

---

## 十、总结：你的问题的直接回答

### Q: 使用docker如果我想用agent执行shell命令在本地电脑上，使用sandbox就是将本地电脑复制到docker，让shell在docker执行，或者是通过ssh在本地电脑执行?

**A: 都不是，正确的方式是：**

1. **不是"复制本地电脑到Docker"**
   ```
   ✗ 这样做太低效，需要复制GB级数据
   ✓ 实际是：用Docker Volume挂载本地目录
   ```

2. **不是"通过SSH在本地电脑执行"**
   ```
   ✗ SSH方式会直接在本地执行，没有隔离
   ✓ 实际是：在容器内执行，容器隔离于本地系统
   ```

3. **正确的方式是：Docker Volume挂载**
   ```
   主机的 /threads/abc/workspace/
       ↓ (volume挂载)
   Docker容器的 /mnt/user-data/workspace/
       ↓ (Agent在容器内看到同样的文件)
   Shell在容器内执行，但操作的是主机的文件
   ```

**具体工作流**：

```
主机文件系统                 Docker容器
/threads/abc/
└─ workspace/
   ├─ data.csv
   ├─ script.py          
   └─ output/

        ↓↑ (Volume挂载)

                         /mnt/user-data/workspace/
                         ├─ data.csv
                         ├─ script.py
                         └─ output/
                         
                         bash-4.4$ python script.py
                         (执行脚本）
                         (数据存储到 output/）
                         
        ↑↓ (Volume挂载)

/threads/abc/outputs/
└─ results.json (出现了！)
```

**安全隔离**：
- Shell命令在容器内执行
- 即使命令是 `rm -rf /`，也只删除容器内的根，主机的文件系统完全不受影响
- 其他用户的容器完全独立

---

**文档生成日期**：2025-04-19  
**版本**：1.0  
**作者**：DeerFlow Sandbox分析

