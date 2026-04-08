"# sparkWorld-AI-Agent" 
1 english character = 0.3
1 chinese character = 0.6

# add tools

uv add fastapi uvicorn[standard] 

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
