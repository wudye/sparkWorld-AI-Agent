我会先做一轮前端只读扫描，确认入口、路由、状态管理、API 调用层和测试链路，再给你一份和 backend 同风格的“从0到1学习报告 + 分阶段计划”。先定位关键文件和调用主线。

Search complete: 定位前端主线

Semantic workspace search is not currently available

Semantic workspace search is not currently available

Searched for files matching `**/frontend/**`, 200 matches

Searched for files matching `**/*.{js,ts,jsx,tsx,mdx}`, 200 matches

Searched for text `next\.js|Next.js|app|pages|routes` (`**/frontend/**`), 200 results

Searched for text `core/services|core/hooks|core/store|business/logic|data layer` (`**/frontend/**`), no results

Searched for text `api.*client|axios.*instance|fetch.*backend|backend.*url|BASE_URL` (`**/frontend/**`), 101 results

Searched for text `package\.json|next\.config\.js|tailwind\.config\.js|eslintrc|jest\.config` (`**/frontend/**`), 11 results

Searched for files matching `**/frontend/**/*.{config,setup,client,provider,store,service,hook}*.{js,ts}`, 6 matches

Searched for files matching `**/frontend/**/*test*.{js,ts,jsx,tsx}`, 5 matches

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/README.md)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/pnpm-workspace.yaml)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/CLAUDE.md)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/AGENTS.md)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/env.js)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/core/config/index.ts)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/next.config.js)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/core/api/api-client.ts)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/core/threads/hooks.ts#1-1), lines 1 to 260

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/core/agents/api.ts)

Searched for files matching `**/src/**`, 200 matches

Searched for files matching `**/tests/**`, 120 matches

Searched for files matching `**/*.md`, 117 matches

Searched for files matching `**/package*.json`, 1 match

Searched for files matching `**/docker*.yml`, no matches

Searched for files matching `**/playwright*.ts`, 1 match

Searched for files matching `**/vitest*.config.*`, 1 match

Searched for files matching `**/next.config.*`, 1 match

Searched for files matching `**/eslintrc*`, no matches

Searched for files matching `**/pnpm-workspace.yaml`, 1 match

我已经拿到前端总体架构和关键文件清单；下一步补齐脚本与真实页面入口（根布局、workspace 布局、线程页）后，就给你一份完整中文学习报告和同样的分阶段学习计划。先补读几个关键源文件。

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/package.json#1-1), lines 1 to 90

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/app)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/core)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/app/layout.tsx)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/app/page.tsx)

当前信息已足够搭建学习框架，我再补两块关键细节：workspace 路由骨架和线程核心 hooks 的其余部分（提交、停止、线程列表/重命名删除），这样你的学习路径会更可执行。读完我就给完整报告。

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/app/workspace)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/core/threads/hooks.ts#160-160), lines 160 to 420

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/core/models/hooks.ts)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/app/workspace/layout.tsx)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/app/workspace/chats)

我发现这个前端没有独立的 “new” 页面，而是通过参数路由处理新会话；我再补读这部分路由和 API 适配细节，确保你的学习地图和实际代码一致。

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/app/workspace/page.tsx)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/core/api/stream-mode.ts)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/core/models/api.ts)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/frontend/src/core/threads/utils.ts)

**Frontend 分析报告（DeerFlow）**

你这个项目的 frontend 不是“普通聊天页面”，而是一个围绕 LangGraph 运行时设计的前端工作台。  
整体可以概括成 4 层：

1. 路由与页面层：Next.js App Router
2. 组件层：workspace/landing/ui 组件组合
3. 核心业务层：src/core（线程、API、模型、上传、技能、设置、i18n 等）
4. 与后端通信层：LangGraph SDK + Gateway API + Next rewrites/proxy

下面我按“先看懂全局，再可动手改代码”的方式讲。

---

**一、Frontend 全局架构**

最核心入口与骨架：

1. 根布局在 layout.tsx  
职责：挂全局样式、主题、i18n provider。

2. 主落地页在 page.tsx  
职责：营销/介绍页面（Hero、Section 等）。

3. 工作区布局在 layout.tsx  
职责：QueryClientProvider、Sidebar、命令面板、Toaster。  
这说明“workspace 才是应用核心壳”。

4. 聊天页主入口在 [frontend/src/app/workspace/chats/[thread_id]/page.tsx](frontend/src/app/workspace/chats/[thread_id]/page.tsx)  
职责：绑定消息列表、输入框、artifact/todo、线程流式交互。

5. 聊天列表页在 page.tsx

路由设计要点：

1. page.tsx 会重定向到 /workspace/chats/new。  
2. 实际上并没有独立的 new 页面文件；new 是 [thread_id] 的一个参数值，由同一个页面组件处理。  
这是一种常见的“单页逻辑 + 参数态”模式。

---

**二、数据流主线（你最该先掌握）**

最关键的链路是：

UI -> thread hooks -> LangGraph SDK stream -> Thread 状态更新 -> 组件重渲染

对应文件：

1. 线程主 hooks 在 hooks.ts  
这是前端“心脏”：  
- useThreadStream  
- optimistic message  
- 文件上传前置  
- stream 事件处理  
- onStart/onFinish/onToolEnd 回调

2. API 客户端在 api-client.ts  
用 LangGraph SDK Client，并对 runs.stream/joinStream 做了 streamMode 兼容清洗。

3. streamMode 适配在 stream-mode.ts  
会过滤不支持的 stream mode，并给 warning。

4. 线程工具函数在 utils.ts  
pathOfThread、titleOfThread、textOfMessage。

这个链路就是你后面做功能时最常碰的链路。

---

**三、前后端通信方式（非常重要）**

有两种通信路径同时存在：

1. 直接走 LangGraph SDK（线程/流式）  
核心在 api-client.ts。

2. 走 Gateway REST（模型、memory、skills 等）  
示例在 api.ts 和 route.ts。

URL 组装与代理策略：

1. 环境变量校验在 env.js。  
2. 基础 URL 逻辑在 index.ts。  
3. Next rewrites 在 next.config.js，当未显式设置 NEXT_PUBLIC_* 时，自动代理到本地 backend/langgraph。  

这部分设计让本地开发无需改太多前端代码即可切换连接目标。

---

**四、组件组织方式**

组件分层比较清晰：

1. 业务组件：workspace  
示例：  
- input-box.tsx  
- recent-chat-list.tsx

2. 基础 UI 组件：ui  
3. AI 相关组件：ai-elements  
4. Landing 展示组件：landing

典型点：聊天主页面把交互编排在 page 里，重逻辑下沉到 core/hooks，组件负责渲染与触发动作，边界比较健康。

---

**五、工程与质量体系**

脚本与门禁来自 package.json：

1. dev: next dev --turbo  
2. build/start  
3. lint/typecheck/check  
4. test（Vitest）  
5. test:e2e（Playwright）

测试结构：

1. 单测示例  
stream-mode.test.ts  
file-validation.test.ts

2. E2E mock 基础设施  
mock-api.ts

这意味着项目很强调“无后端依赖也能测 UI 行为”的稳定性。

---

**六、你做“同样学习”的推荐路径（Frontend 版）**

**第 1 阶段：跑通与识图（1-2 天）**
1. 读 README.md 和 CLAUDE.md。  
2. 跑 dev、lint、typecheck、test。  
3. 画一张页面流转图：/ -> /workspace -> /workspace/chats/[thread_id]。

**第 2 阶段：线程与流式（2-4 天）**
1. 深读 hooks.ts。  
2. 对照 [frontend/src/app/workspace/chats/[thread_id]/page.tsx](frontend/src/app/workspace/chats/[thread_id]/page.tsx)。  
3. 理解 onCreated/onUpdate/onFinish 与 optimistic message 的关系。  
目标：你能解释“发一条消息后，前端状态如何变化”。

**第 3 阶段：通信与配置（2-3 天）**
1. 深读 api-client.ts 与 stream-mode.ts。  
2. 深读 index.ts、env.js、next.config.js。  
目标：你能独立排查“前端连错后端地址”这类问题。

**第 4 阶段：组件与交互（3-5 天）**
1. 深读 input-box.tsx。  
2. 深读 recent-chat-list.tsx。  
3. 做一个小改动：加一个输入模式或列表操作并跑单测。  

**第 5 阶段：测试反推实现（持续）**
1. 先看测试，再回源码。  
2. 从 stream-mode、upload、thread 相关测试开始。  
目标：养成“改动前先有断言”的节奏。

---

**七、你现在就可以做的第一周计划（简版）**

1. Day 1：读 layout.tsx、layout.tsx、[frontend/src/app/workspace/chats/[thread_id]/page.tsx](frontend/src/app/workspace/chats/[thread_id]/page.tsx)。  
2. Day 2：读 hooks.ts 前半，画消息发送时序图。  
3. Day 3：读 hooks 后半，重点看上传、错误处理、finish 回调。  
4. Day 4：读 api-client.ts + stream-mode.ts。  
5. Day 5：读 index.ts、env.js、next.config.js。  
6. Day 6：读 2-3 个 workspace 组件，梳理 props 与状态来源。  
7. Day 7：跑 test + e2e，挑一个小点做改动并验证。

---

如果你愿意，我下一步可以直接给你“Frontend Day 1 的逐文件精读清单”，按 60-90 分钟节奏拆成可执行任务。