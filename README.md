"# sparkWorld-AI-Agent" 
1 english character = 0.3
1 chinese character = 0.6

# add tools


uv add transformers to check token length

对于 DeepSeek 模型来说,消息列表中支持4种角色:system、 user, assistant, tool,这些角色有着
不同的作用,并且排列顺序有着严格的规定:
system：系统设定，一般用于预设LLM的一些基础行为、响应风格、回复风格等
user: 用户的输入/指令的输入:
assistant: AI的回复/思考、工作调用参数生成:
tool: 工具的执行结果;

# token estimate 
1. transformers + jieja2(Chinese)
1个英文字符 0.3个token.
1个中文字符 0.6个token.
2. online https://platform.openai.com/tokenizer

# CoT(chain of thought) thought chain

set stream=True, response is a generator of streamed chunks.
Each chunk is a ChatCompletionChunk object from the OpenAI client.
Each chunk has:
chunk.id
chunk.created
chunk.model
chunk.choices (a list)

Each element of chunk.choices is a Choice object for streaming, and it has a field named delta.

For streaming, the API does not send the full final message each time.
Instead, it sends small pieces (deltas) that you are supposed to accumulate.
So:
delta = “only what changed in this step” (a partial update)
final non-streaming object = full message with all fields filled
In code terms, delta is an object that may contain:
delta.content – a small piece of text (sometimes just one token or a few characters)
delta.role – possibly set only in the first chunk
delta.tool_calls – pieces of tool call information
and some other optional fields


 类比：采样率就像"每秒拍多少张照片"。16kHz 就是每秒对声音采样 16000 次。CD 音质是 44100Hz，但语音识别不需要那么高。

                        Voice Agent Process                         
    👤 User input voice                                                         
             │                                                                
             ▼                                                                
   ┌──────────────────────┐                                           
   │   🎤 Agent #1: STT   │  ← Whisper-tiny (HuggingFace)            
   │   Speech → Text      │     model: openai/whisper-tiny           
   │                      │     running: GPU/CPU locally                   
   └──────────┬───────────┘                                           
              │ "One hundred plus two hundred"                         
              ▼                                                       
   ┌──────────────────────┐                                           
   │   🧠 Agent #2: LLM   │  ← Gemma4:e2b (via Ollama)              
   │   Text → Reasoning   │     base_url: localhost:11434            
   │   + Tool Use         │     use ReAct model               
   │                      │                                          
   │   ┌────────────────┐ │     tool: calculator                     
   │   │  calculator()  │ │     input: "100 + 200"                    
   │   └────────────────┘ │     output: 300                             
   └──────────┬───────────┘                                           
              │ "Assistant: 300"                                       
              ▼                                                       
   ┌──────────────────────┐                                           
   │   🔊 Agent #3: TTS    │  ← speecht5_tts/Edge TTS (Microsoft Azure)           
   │   Text → Speech       │     voice: en-US-AriaNeural              
   │                       │     running: GPU/CPU           locally  
   └──────────┬───────────┘                                           
              ▼                                                        
   🔊 user hears "Assistant: 300"


Deploy a Local Voice Agent on Your PC (Free & Safe)

This small demo project wires together **three “agents”** to build an end‑to‑end voice assistant that runs entirely on your **local PC**:

1. **Agent #1 – STT (Speech to Text)**  
   - Listens to your microphone, records audio, and converts it into text.  
   - Uses **Whisper‑tiny** from Hugging Face:  
     - Model: `openai/whisper-tiny`  
     - Runs locally on **CPU or GPU** (no network calls in STT path).  

2. **Agent #2 – LLM + Tools (Reasoning)**  
   - Takes the transcribed text and lets a local LLM reason about it.  
   - Uses **Gemma4:e2b** via **Ollama**:  
     - Base URL: `http://localhost:11434`  
     - OpenAI‑compatible `/v1/chat/completions` endpoint.  
   - Implements a simple **ReAct‑style tool calling**:
     - Tool: `calculator(expression: str) -> str`
       - Evaluates basic math expressions, returning JSON like `{"result": 300}`.
     - The agent:
       1. Sends user text + tool schema to the LLM.
       2. LLM decides whether to call `calculator`.
       3. Python executes the tool and returns its result as a `"tool"` message.
       4. LLM uses the tool result to produce the final natural‑language answer.

3. **Agent #3 – TTS (Text to Speech)**  
   - Converts the LLM’s final text answer back into speech.  
   - Two implementations are provided:
     - **Local neural TTS** using Microsoft SpeechT5:  
       - Models:  
         - `microsoft/speecht5_tts` (acoustic model)  
         - `microsoft/speecht5_hifigan` (vocoder)  
       - Runs locally on CPU/GPU (no network).
     - **Edge TTS (optional, online)** using `edge_tts`:  
       - Example voice: `en-US-AriaNeural`.  
       - Requires Internet and calls Microsoft TTS; not strictly “offline”.

For a **fully local / free / privacy‑preserving** setup, you can:

- Use Whisper‑tiny (HF) for STT.
- Use Gemma4:e2b (Ollama) for reasoning + tools.
- Use SpeechT5 for TTS.
- Disable the Edge TTS path.
