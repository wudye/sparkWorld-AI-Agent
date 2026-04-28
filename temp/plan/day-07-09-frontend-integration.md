# Day 7-9: 前端集成与实时通信

**日期**: Day 7-9 (第七-九天)  
**目标**: 实现前端与后端 API 通信、实时流处理、状态管理  
**预计时间**: 8-10 小时  
**难度**: ⭐⭐⭐ (较难)  
**前置**: 完成 Day 4-6  

---

## 📋 学习概念

### 1. Server-Sent Events (SSE) 深入理解

**SSE vs WebSocket**:
| 特性 | SSE | WebSocket |
|------|-----|----------|
| 连接方向 | 单向(服务器→客户端) | 双向 |
| 自动重连 | ✓ 内置 | ✗ 需手动实现 |
| 文本格式 | ✓ 易于调试 | ✗ 二进制 |
| 复杂度 | ✓ 简单 | ✗ 复杂 |
| 最优用例 | 推送通知、流式更新 | 即时双向通信 |

**DeerFlow 选择 SSE 的原因**:
- 后端只需推送（无需处理复杂的双向消息）
- 更容易与 REST API 集成
- 浏览器内置支持，无特殊库

### 2. React Query（TanStack Query）

**核心概念**:
- **Query**: 获取数据（GET 请求）
- **Mutation**: 修改数据（POST/PUT/DELETE）
- **Cache**: 自动缓存管理
- **Background Refetch**: 后台自动更新

### 3. Zustand 状态管理

**简化的 Redux 替代品**:
- 轻量级（仅 2KB）
- 无需 Provider（可选）
- TypeScript 友好

### 4. 流式处理与实时更新

**架构**:
```
用户输入 → API 请求 → SSE 连接（保持打开）
                        ↓ (流式事件)
                     解析JSON → 更新 UI
```

---

## 🛠️ Part 1: 状态管理设置（Day 7 上午）

### 1.1 创建 Thread Store（Zustand）

创建 `frontend/src/core/store/useThreadStore.ts`:

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface Thread {
  id: string;
  title?: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  modelId?: string;
}

interface ThreadStore {
  // State
  threads: Thread[];
  currentThreadId: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setCurrentThread: (threadId: string | null) => void;
  addThread: (thread: Thread) => void;
  updateThread: (threadId: string, thread: Partial<Thread>) => void;
  deleteThread: (threadId: string) => void;
  addMessage: (threadId: string, message: Message) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  clearAll: () => void;
}

export const useThreadStore = create<ThreadStore>()(
  persist(
    (set) => ({
      threads: [],
      currentThreadId: null,
      isLoading: false,
      error: null,

      setCurrentThread: (threadId) =>
        set({ currentThreadId: threadId }),

      addThread: (thread) =>
        set((state) => ({ threads: [thread, ...state.threads] })),

      updateThread: (threadId, updates) =>
        set((state) => ({
          threads: state.threads.map((t) =>
            t.id === threadId ? { ...t, ...updates } : t
          ),
        })),

      deleteThread: (threadId) =>
        set((state) => ({
          threads: state.threads.filter((t) => t.id !== threadId),
          currentThreadId:
            state.currentThreadId === threadId ? null : state.currentThreadId,
        })),

      addMessage: (threadId, message) =>
        set((state) => ({
          threads: state.threads.map((t) =>
            t.id === threadId
              ? { ...t, messages: [...t.messages, message] }
              : t
          ),
        })),

      setError: (error) => set({ error }),

      setLoading: (loading) => set({ isLoading: loading }),

      clearAll: () =>
        set({
          threads: [],
          currentThreadId: null,
          isLoading: false,
          error: null,
        }),
    }),
    {
      name: 'thread-store',
      skipHydration: true,
    }
  )
);

// Selectors（性能优化）
export const useCurrentThread = () =>
  useThreadStore((state) => {
    const threadId = state.currentThreadId;
    return state.threads.find((t) => t.id === threadId);
  });

export const useThreadMessages = (threadId?: string) =>
  useThreadStore((state) => {
    const id = threadId || state.currentThreadId;
    if (!id) return [];
    return state.threads.find((t) => t.id === id)?.messages || [];
  });
```

### 1.2 创建 Model Store

创建 `frontend/src/core/store/useModelStore.ts`:

```typescript
import { create } from 'zustand';

export interface Model {
  id: string;
  name: string;
  provider: string;
  capabilities: string[];
  contextWindow: number;
  costPer1kTokens: number;
}

interface ModelStore {
  models: Model[];
  selectedModelId: string | null;
  setModels: (models: Model[]) => void;
  setSelectedModel: (modelId: string) => void;
}

export const useModelStore = create<ModelStore>((set) => ({
  models: [],
  selectedModelId: null,

  setModels: (models) => set({ models }),

  setSelectedModel: (modelId) =>
    set((state) => ({
      selectedModelId:
        state.models.find((m) => m.id === modelId) ? modelId : null,
    })),
}));

export const useSelectedModel = () =>
  useModelStore((state) => {
    const modelId = state.selectedModelId;
    return state.models.find((m) => m.id === modelId);
  });
```

---

## 🔌 Part 2: API 集成层（Day 7 下午）

### 2.1 创建 React Query 配置

创建 `frontend/src/core/api/queryClient.ts`:

```typescript
import {
  QueryClient,
  defaultShouldDehydrateQuery,
  isServer,
} from '@tanstack/react-query';

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,        // 60秒内数据被认为是新鲜的
        gcTime: 10 * 60 * 1000,      // 10分钟后清理不使用的数据
        retry: 1,                     // 失败重试 1 次
        throwOnError: true,
      },
      mutations: {
        retry: 1,
      },
      dehydrate: {
        shouldDehydrateQuery(query) {
          return (
            defaultShouldDehydrateQuery(query) ||
            query.state.status === 'pending'
          );
        },
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined;

export function getQueryClient() {
  if (isServer) {
    return makeQueryClient();
  } else {
    if (!browserQueryClient) {
      browserQueryClient = makeQueryClient();
    }
    return browserQueryClient;
  }
}

export const queryClient = getQueryClient();
```

### 2.2 创建 API Hooks

创建 `frontend/src/core/api/hooks.ts`:

```typescript
import { useMutation, useQuery } from '@tanstack/react-query';
import { useCallback } from 'react';
import { Thread, Message } from '@/core/store/useThreadStore';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

/**
 * 获取所有模型
 */
export function useModels() {
  return useQuery({
    queryKey: ['models'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/api/models`);
      if (!response.ok) throw new Error('获取模型失败');
      return response.json();
    },
  });
}

/**
 * 创建对话线程
 */
export function useCreateThread() {
  return useMutation({
    mutationFn: async (config?: Record<string, any>) => {
      const response = await fetch(`${API_BASE}/api/langgraph/threads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config: config || {} }),
      });
      if (!response.ok) throw new Error('创建线程失败');
      return response.json();
    },
  });
}

/**
 * 流式获取对话事件
 */
export function useStreamThreadEvents() {
  return useCallback(
    async function* (threadId: string, input: string) {
      const response = await fetch(
        `${API_BASE}/api/langgraph/threads/${threadId}/events`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'text/event-stream',
          },
          body: JSON.stringify({ input }),
        }
      );

      if (!response.ok) {
        throw new Error('流式请求失败');
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('无法获取响应流');

      const decoder = new TextDecoder();
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');

          // 保留最后一个不完整的行
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('event:')) {
              // 处理事件类型行
              continue;
            }
            if (line.startsWith('data:')) {
              const data = line.slice(5).trim();
              if (data) {
                try {
                  yield JSON.parse(data);\n                } catch (e) {\n                  console.error('JSON 解析失败:', e, data);\n                }\n              }\n            }\n          }\n        }\n      } finally {\n        reader.releaseLock();\n      }\n    },\n    []\n  );\n}\n\n/**\n * 获取线程状态\n */\nexport function useThreadState(threadId: string) {\n  return useQuery({\n    queryKey: ['thread', threadId, 'state'],\n    queryFn: async () => {\n      const response = await fetch(\n        `${API_BASE}/api/langgraph/threads/${threadId}/state`\n      );\n      if (!response.ok) throw new Error('获取线程状态失败');\n      return response.json();\n    },\n    enabled: !!threadId,\n  });\n}\n```\n\n---\n\n## 💬 Part 3: 聊天界面实现（Day 8）\n\n### 3.1 创建消息列表组件\n\n创建 `frontend/src/components/chat/MessageList.tsx`:\n\n```typescript\n'use client';\n\nimport { useThreadMessages } from '@/core/store/useThreadStore';\nimport { Message } from '@/core/store/useThreadStore';\nimport { Fragment } from 'react';\n\nexport interface MessageListProps {\n  threadId: string;\n}\n\nfunction MessageItem({ message }: { message: Message }) {\n  const isUser = message.role === 'user';\n\n  return (\n    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>\n      <div\n        className={`max-w-md px-4 py-2 rounded-lg ${\n          isUser\n            ? 'bg-blue-500 text-white'\n            : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100'\n        }`}\n      >\n        <p className=\"whitespace-pre-wrap text-sm\">{message.content}</p>\n        <span className=\"text-xs opacity-70 mt-1 block\">\n          {message.timestamp.toLocaleTimeString()}\n        </span>\n      </div>\n    </div>\n  );\n}\n\nexport function MessageList({ threadId }: MessageListProps) {\n  const messages = useThreadMessages(threadId);\n\n  return (\n    <div className=\"flex-1 overflow-y-auto p-4 space-y-4\">\n      {messages.length === 0 ? (\n        <div className=\"flex items-center justify-center h-full text-gray-500\">\n          <p>没有消息。开始一个新对话吧！</p>\n        </div>\n      ) : (\n        messages.map((message) => (\n          <Fragment key={message.id}>\n            <MessageItem message={message} />\n          </Fragment>\n        ))\n      )}\n    </div>\n  );\n}\n```\n\n### 3.2 创建消息输入组件\n\n创建 `frontend/src/components/chat/MessageInput.tsx`:\n\n```typescript\n'use client';\n\nimport { useState, useRef, useEffect } from 'react';\nimport { Send, Plus } from 'lucide-react';\nimport { Button } from '@/components/ui/Button';\n\nexport interface MessageInputProps {\n  onSubmit: (message: string) => Promise<void>;\n  disabled?: boolean;\n}\n\nexport function MessageInput({\n  onSubmit,\n  disabled = false,\n}: MessageInputProps) {\n  const [message, setMessage] = useState('');\n  const [isSubmitting, setIsSubmitting] = useState(false);\n  const textareaRef = useRef<HTMLTextAreaElement>(null);\n\n  // 自动调整 textarea 高度\n  useEffect(() => {\n    if (textareaRef.current) {\n      textareaRef.current.style.height = 'auto';\n      textareaRef.current.style.height = Math.min(\n        textareaRef.current.scrollHeight,\n        120\n      ) + 'px';\n    }\n  }, [message]);\n\n  const handleSubmit = async (e: React.FormEvent) => {\n    e.preventDefault();\n    if (!message.trim() || isSubmitting || disabled) return;\n\n    setIsSubmitting(true);\n    try {\n      await onSubmit(message);\n      setMessage('');\n    } finally {\n      setIsSubmitting(false);\n    }\n  };\n\n  const handleKeyDown = (e: React.KeyboardEvent) => {\n    if (e.key === 'Enter' && e.ctrlKey) {\n      handleSubmit(e as any);\n    }\n  };\n\n  return (\n    <form onSubmit={handleSubmit} className=\"border-t border-gray-200 dark:border-gray-800 p-4 space-y-3\">\n      <div className=\"flex gap-2\">\n        <button\n          type=\"button\"\n          disabled={disabled || isSubmitting}\n          className=\"p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition disabled:opacity-50\"\n        >\n          <Plus className=\"w-5 h-5\" />\n        </button>\n        <textarea\n          ref={textareaRef}\n          value={message}\n          onChange={(e) => setMessage(e.target.value)}\n          onKeyDown={handleKeyDown}\n          placeholder=\"输入消息... (Ctrl+Enter 发送)\"\n          disabled={disabled || isSubmitting}\n          className=\"flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg dark:bg-gray-900 dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-blue-500\"\n          rows={1}\n        />\n        <Button\n          type=\"submit\"\n          disabled={!message.trim() || isSubmitting || disabled}\n          className=\"px-4\"\n        >\n          <Send className=\"w-4 h-4\" />\n        </Button>\n      </div>\n      <p className=\"text-xs text-gray-500\">\n        Ctrl+Enter 发送\n      </p>\n    </form>\n  );\n}\n```\n\n---\n\n## 🔄 Part 4: 流式通信集成（Day 9）\n\n### 4.1 创建聊天主组件\n\n创建 `frontend/src/components/chat/ChatWindow.tsx`:\n\n```typescript\n'use client';\n\nimport { useState, useCallback } from 'react';\nimport { useThreadStore, useCurrentThread } from '@/core/store/useThreadStore';\nimport { useStreamThreadEvents } from '@/core/api/hooks';\nimport { MessageList } from './MessageList';\nimport { MessageInput } from './MessageInput';\nimport { v4 as uuidv4 } from 'uuid';\n\nexport function ChatWindow() {\n  const currentThread = useCurrentThread();\n  const { addMessage, updateThread } = useThreadStore();\n  const streamEvents = useStreamThreadEvents();\n  const [isLoading, setIsLoading] = useState(false);\n\n  const handleSendMessage = useCallback(\n    async (content: string) => {\n      if (!currentThread) return;\n\n      const threadId = currentThread.id;\n\n      // 1. 立即显示用户消息\n      addMessage(threadId, {\n        id: uuidv4(),\n        role: 'user',\n        content,\n        timestamp: new Date(),\n      });\n\n      setIsLoading(true);\n\n      try {\n        let assistantMessage = '';\n        let assistantId = uuidv4();\n\n        // 2. 流式接收助手消息\n        for await (const event of streamEvents(threadId, content)) {\n          if (event.type === 'message') {\n            assistantMessage = event.data.content || '';\n\n            // 实时更新或创建助手消息\n            const existingMessages = currentThread.messages.filter(\n              (m) => m.id === assistantId\n            );\n            if (existingMessages.length > 0) {\n              // 更新现有消息\n              addMessage(threadId, {\n                id: assistantId,\n                role: 'assistant',\n                content: assistantMessage,\n                timestamp: new Date(),\n              });\n            } else {\n              // 创建新消息\n              addMessage(threadId, {\n                id: assistantId,\n                role: 'assistant',\n                content: assistantMessage,\n                timestamp: new Date(),\n              });\n            }\n          } else if (event.type === 'function_call') {\n            // 处理工具调用\n            console.log('Tool call:', event.data);\n          } else if (event.type === 'end') {\n            // 流结束\n            break;\n          }\n        }\n      } catch (error) {\n        console.error('流式通信错误:', error);\n        addMessage(threadId, {\n          id: uuidv4(),\n          role: 'system',\n          content: `错误: ${error instanceof Error ? error.message : '未知错误'}`,\n          timestamp: new Date(),\n        });\n      } finally {\n        setIsLoading(false);\n      }\n    },\n    [currentThread, streamEvents, addMessage]\n  );\n\n  if (!currentThread) {\n    return (\n      <div className=\"flex items-center justify-center h-full text-gray-500\">\n        <p>没有选中对话。请从左侧选择一个对话。</p>\n      </div>\n    );\n  }\n\n  return (\n    <div className=\"flex flex-col h-full bg-white dark:bg-gray-900\">\n      {/* 聊天头部 */}\n      <div className=\"border-b border-gray-200 dark:border-gray-800 p-4\">\n        <h2 className=\"text-lg font-semibold\">\n          {currentThread.title || 'Untitled'}\n        </h2>\n      </div>\n\n      {/* 消息列表 */}\n      <MessageList threadId={currentThread.id} />\n\n      {/* 消息输入 */}\n      <MessageInput onSubmit={handleSendMessage} disabled={isLoading} />\n    </div>\n  );\n}\n```\n\n---\n\n## ✅ 实战检查清单\n\n- [ ] Zustand Store 创建完毕\n- [ ] React Query 配置完毕\n- [ ] API Hooks 实现完毕\n- [ ] 能够成功连接到后端\n- [ ] SSE 流式事件正确解析\n- [ ] 聊天界面能实时显示消息\n- [ ] 消息输入和发送功能正常\n- [ ] 浏览器控制台无错误\n\n---\n\n## ⏱️ 时间记录\n\n| 阶段 | 预计时间 | 实际时间 |\n|------|---------|----------|\n| Part 1: 状态管理 (Day 7 AM) | 2 小时 | ___ |\n| Part 2: API 集成 (Day 7 PM) | 2 小时 | ___ |\n| Part 3: 聊天界面 (Day 8) | 2 小时 | ___ |\n| Part 4: 流式通信 (Day 9) | 2 小时 | ___ |\n| **总计** | **8-10 小时** | **___** |\n\n---\n\n**下一步**: 完成后，进入 Day 10-11 - 后端网关与基础路由\n"
