The user wants me to summarize the three key technical steps in building a voice agent:
1. How to define a tool and have the agent use it
2. How to convert voice to text (STT)
3. How to convert text to voice (TTS)

They want the technical steps for each. Let me organize this clearly based on their actual code.
完全正确！这就是构建 Voice AI Agent 的**三大核心技术点**。让我从代码中提取每个点的具体技术步骤：

---

# 技术点一：定义工具 & Agent 使用工具（ReAct 模式）

## 技术步骤

```
Step 1: 定义工具函数
   ↓
Step 2: 注册工具的 JSON Schema（描述给 LLM 看）
   ↓
Step 3: 发送请求时带上 tools 参数
   ↓
Step 4: 解析 LLM 返回的 tool_calls
   ↓
Step 5: 执行工具函数
   ↓
Step 6: 将结果回传给 LLM，生成最终回答
```

### Step 1：定义工具函数

```49:55:H:\sparkworld\ basicKnowledge\8voiceAgent.py
def calculator(expression: str) -> str:
    """a simple calculator tool demo"""
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"Invalid expression: {e}"})
```

**要点：**
- 函数接收 **字符串参数**，返回 **JSON 字符串**
- 用 `json.dumps()` 包装返回值——LLM 能更好地理解结构化数据
- 必须有 **docstring** —— 后面会自动填入 Schema 的 `description`

### Step 2：注册工具的 JSON Schema（告诉 LLM "你有这个工具"）

```71:90:H:\sparkworld\ basicKnowledge\8voiceAgent.py
self.tool = [
    {
        "type": "function",
        "function": {
            "name": "calculator",           # ← 工具名（必须和函数名一致）
            "description": "A simple calculator tool that evaluates basic math expressions.",
            "parameters": {                 # ← 描述参数格式（JSON Schema）
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate, e.g., '2 + 2'."
                    }
                },
                "required": ["expression"]  # ← 标记必填参数
            }
        }
    }
]
```

同时把函数注册到可用工具字典：

```71:H:\sparkworld\ basicKnowledge\8voiceAgent.py
self.available_tools = {"calculator": calculator}
```

**Schema 的作用：LLM 看到 description 后，知道什么时候该调用这个工具、怎么构造参数。**

### Step 3：发送请求时携带 tools 参数

```96:101:H:\sparkworld\ basicKnowledge\8voiceAgent.py
response = self.client.chat.completions.create(
    model=self.model,
    messages=self.messages,
    tools=self.tool,          # ← 关键！把工具列表传进去
    stream=False
)
```

**这一步之后，LLM 会自己决定：是直接回答？还是调用工具？**

### Step 4：解析 LLM 返回的 tool_calls

```103:104:H:\sparkworld\ basicKnowledge\8voiceAgent.py
response_message = response.choices[0].message
tool_calls = response_message.tool_calls     # ← 如果 LLM 决定调用工具，这里不为空
```

如果 LLM 选择直接回答 → `tool_calls = None` → 跳到 Step 6  
如果 LLM 选择调用工具 → `tool_calls` 包含工具名和参数 → 继续 Step 5

**tool_calls 的结构：**

```python
tool_calls = [
    ChoiceDeltaToolCall(
        id="call_abc123",              # 工具调用唯一 ID
        function=Function(
            name="calculator",         # 要调用的工具名
            arguments='{"expression": "100 + 200"}'   # JSON 字符串形式的参数
        )
    )
]
```

### Step 5：执行工具函数

```108:123:H:\sparkworld\ basicKnowledge\8voiceAgent.py
if tool_calls:
    for tool_call in tool_calls:
        print("tool call", tool_call.function.name)
        tool_name = tool_call.function.name                    # "calculator"
        tool_args = json.loads(tool_call.function.arguments)   # {"expression": "100 + 200"}

        function_to_call = self.available_tools[tool_name]      # 找到 calculator 函数

        result = function_to_call(**tool_args)                  # 执行！→ '{"result": 300}'
        print(f"tool [{tool_name}] result: {result}")

        # 把工具执行结果作为消息追加到对话历史中
        self.messages.append({
            "tool_call_id": tool_call.id,   # 关联到上面的调用请求
            "role": "tool",                  # 特殊角色："tool"
            "name": tool_name,
            "content": result                # 工具返回值
        })
```

**关键：消息必须追加到对话历史！LLM 需要看到工具返回了什么才能继续推理。**

### Step 6：再次请求 LLM 生成最终回答

```125:133:H:\sparkworld\ basicKnowledge\8voiceAgent.py
second_response = self.client.chat.completions.create(
    model=self.model,
    messages=self.messages,       # ← 现在包含了工具调用 + 工具结果
    tools=self.tool,
    stream=False
)
second_response_message = second_response.choices[0].message
return "Assistant: " + second_response_message.content
```

---

### 完整 ReAct 数据流图

```
messages 历史记录变化:

初始状态:
┌─────────────────────────────────┐
│ {"role": "system", ...}         │
│ {"role": "user": "100+200"}     │  ← 用户问题
└──────────────┬──────────────────┘
               │ create() 带 tools
               ▼
第 1 次 LLM 返回 (决定用工具):
┌─────────────────────────────────┐
│ {"role": "system", ...}         │
│ {"role": "user": "100+200"}     │
│ {"role": "assistant",           │  ← LLM 说：我要调用 calculator
│   tool_calls: [...]}            │
└──────────────┬──────────────────┘
               │ 追加 tool 结果
               ▼
第 2 次 LLM 返回 (生成最终答案):
┌─────────────────────────────────┐
│ {"role": "system", ...}         │
│ {"role": "user": "100+200"}     │
│ {"role": "assistant",           │
│   tool_calls: [...]}            │
│ {"role": "tool",                │  ← 工具执行结果: 300
│   "300"}                        │
│ {"role": "assistant",           │  ← LLM 最终回答
│   "300"}                        │
└─────────────────────────────────┘
```

---

# 技术点二：语音转文字（STT）

## 技术步骤

```
Step 1: 配置音频采集参数
   ↓
Step 2: 创建音频输入流（后台持续采集）
   ↓
Step 3: 用户按空格 → 开始录音（回调函数收集数据块）
   ↓
Step 4: 用户再按空格 → 停止录音
   ↓
Step 5: 拼接所有音频块 → NumPy 数组
   ↓
Step 6: 处理维度/声道（确保单声道一维）
   ↓
Step 7: 写入临时 WAV 文件
   ↓
Step 8: 调用 Whisper Pipeline 转写
   ↓
Step 9: 返回文字
```

### Step 1-2：配置采集 + 启动流

```205:239:H:\sparkworld\ basicKnowledge\8voiceAgent.py
@classmethod
def speech_to_text(cls) -> str:

    samplerrate = 16000       # Whisper 要求 16kHz
    channels = 1              # 单声道
    recording = []             # 存放音频数据块
    is_recording = False       # 录音开关

    def callback(indata, frames, time, status):
        if is_recording:
            recording.append(indata.copy())   # 只在录音状态才保存

    stream = sd.InputStream(samplerate=samplerrate, channels=channels, callback=callback)
    stream.start()             # 后台线程开始采集（此时还不录音）
```

**关键技术点：回调模式（Callback Pattern）**

```
麦克风硬件
    │
    ▼ (每秒 ~15 次)
InputStream 内部循环
    │
    ▼
callback(indata, frames, time, status)
    │
    ├── is_recording=False? → 丢弃数据
    └── is_recording=True?  → recording.append(indata.copy())
```

### Step 3-4：按键控制录音起停

```250:258:H:\sparkworld\ basicKnowledge\8voiceAgent.py
keyboard.wait("space")       # 阻塞等待第一次空格
is_recording = True          # 开始收集数据
print("Recording, press space to stop...")

keyboard.wait("space")       # 阻塞等待第二次空格
is_recording = False         # 停止收集
stream.stop()
stream.close()
```

### Step 5-6：数据处理

```264:269:H:\sparkworld\ basicKnowledge\8voiceAgent.py
audio_data = np.concatenate(recording, axis=0)    # [块1, 块2, ..., 块N] → 一个长数组

if audio_data.ndim > 1:
    if audio_data.shape[1] > 1:
        audio_data = np.mean(audio_data, axis=1)   # 多声道取平均值
    audio_data = audio_data.flatten()               # 强制变一维
```

### Step 7-9：写入文件 + Whisper 转写

```271:280:H:\sparkworld\ basicKnowledge\8voiceAgent.py
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
    sf.write(temp_audio_file.name, audio_data, samplerrate)  # NumPy → WAV 文件
    audio_path = temp_audio_file.name

transcription = stt_from_wav_file(audio_path)   # WAV → Whisper → 文字
print("Transcription:", transcription)
return transcription
```

底层调用的 pipeline 函数：

```43:46:H:\sparkworld\ basicKnowledge\8voiceAgent.py
def stt_from_wav_file(path: str) -> str:
    result = stt_pipe(path)           # transformers pipeline 自动处理
    return result["text"]
```

---

### STT 完整数据变换链

```
声波 (空气振动)
    │
    ▼
麦克风 (模拟信号)
    │
    ▼ sounddevice (ADC)
NumPy 数组 float64 (frames, channels)
    │
    ▼ np.concatenate()
完整音频数组 shape(N, 1) 或 (N,)
    │
    ▼ sf.write()
WAV 文件 (磁盘上)
    │
    ▼ stt_pipeline() / Whisper
文字字符串: "100 plus 200"
```

---

# 技术点三：文字转语音（TTS）

## 技术步骤（Edge TTS 版本）

```
Step 1: 清理文本（去掉前缀、特殊字符）
   ↓
Step 2: 选择音色 (Voice)
   ↓
Step 3: 创建 Edge TTS Communicate 对象
   ↓
Step 4: 异步调用微软 API 生成 MP3
   ↓
Step 5: 读取 MP3 音频文件
   ↓
Step 6: 通过扬声器播放
```

### Step 1：清理文本

```347:H:\sparkworld\ basicKnowledge\8voiceAgent.py
clean_text = text.replace("Assistant:", "").replace("$", "").strip()
```

**原因：** Agent 输出带有 `"Assistant: "` 前缀和可能的 LaTeX 符号，TTS 引擎不需要这些。

### Step 2：选择音色

```348:H:\sparkworld\ basicKnowledge\8voiceAgent.py
voice = "en-US-AriaNeural"
```

### Step 3：创建 Communicate 对象

```351:H:\sparkworld\ basicKnowledge\8voiceAgent.py
communicate = edge_tts.Communicate(text=clean_text, voice=voice)
```

**注意：此时还没有联网！只是封装了参数。**

### Step 4：异步生成 MP3

```352:354:H:\sparkworld\ basicKnowledge\8voiceAgent.py
asyncio.get_event_loop().run_until_complete(
    communicate.save("temp_output.mp3")
)
```

内部发生的事：
```
你的 Python 进程
    │
    ▼ asyncio.run_until_complete()
异步任务启动
    │
    ▼ HTTPS POST
Microsoft Azure TTS API (免费)
    │
    ▼ SSML 格式请求
<speak version="1.0">
  <voice name="en-US-AriaNeural">
    300
  </voice>
</speak>
    │
    ▼ HTTP Response (流式)
MP3 音频数据 (分块到达)
    │
    ▼ 写入磁盘
temp_output.mp3
```

### Step 5-6：读取并播放

```356:358:H:\sparkworld\ basicKnowledge\8voiceAgent.py
data, samplerate = sf.read("temp_output.mp3")   # MP3 → NumPy 数组
sd.play(data, samplerate)                        # NumPy → 扬声器
sd.wait()                                        # 等待播放完毕
```

---

### TTS 完整数据变换链

```
Agent 回答文本: "Assistant: 300"
    │
    ▼ 清理
纯文本: "300"
    │
    ▼ edge_tts.Communicate()
HTTP 请求 → 微软 Azure TTS 服务
    │
    ▼ 返回 MP3 流
MP3 文件 (磁盘上, 压缩格式)
    │
    ▼ sf.read()
NumPy 数组 float64 (PCM 解码后)
    │
    ▼ sd.play() → 声卡 DAC
声波 (扬声器振动) 🔊
```

---

# 三大技术点总结

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  🔧 技术点一: Tool Use (ReAct)                                   │
│  ─────────────────────────────                                   │
│  定义函数 → JSON Schema → 发tools → 解析tool_calls → 执行 → 回传 │
│                                                                  │
│  🎤 技术点二: STT (Speech-to-Text)                               │
│  ─────────────────────────────────                                │
│  录音(回调模式) → 拼接NumPy → 写WAV → Whisper转写 → 文字          │
│                                                                  │
│  🔊 技术点三: TTS (Text-to-Speech)                               │
│  ───────────────────────────────                                  │
│  清理文本 → 选音色 → Edge TTS API(MP3) → 读取 → 播放             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

| 技术点 | 输入 | 输出 | 核心库 | 运行位置 |
|--------|------|------|--------|---------|
| **Tool Use** | 用户问题文本 | 助手回答文本 | OpenAI SDK + Ollama | 本地 (localhost:11434) |
| **STT** | 麦克风音频 | 文字字符串 | sounddevice + transformers | 本地 GPU/CPU |
| **TTS** | 助手回答文本 | 扬声器声音 | edge-tts + sounddevice | 云端 (Microsoft Azure) |

这三个技术点是构建任何 **Voice AI Agent** 的通用模式。掌握了它们，你就可以自由组合和扩展了！还有什么想深入的吗？