# DeerFlow Frontend 14天实战学习计划

目标：从“能看懂项目”进阶到“可独立复刻核心前端链路”。

学习原则：

- 先打通主链路，再补充高级能力
- 每天都有可验证产出
- 读源码与动手实现并重（建议 3:7）

---

## Day 1：跑通项目与入口认知

### 阅读

- `frontend/README.md`
- `frontend/package.json`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/workspace/layout.tsx`

### 实战

- 本地启动前端
- 理解 RootLayout 与 WorkspaceLayout 的职责差异

### 验收

- 能进入 `/workspace`
- 能口述 Provider 结构（Theme、i18n、Query、Sidebar、Toaster）

---

## Day 2：环境变量与代理机制

### 阅读

- `frontend/src/env.js`
- `frontend/next.config.js`
- `frontend/src/core/config/index.ts`

### 实战

- 画出请求路径决策图：直连 vs rewrite

### 验收

- 能解释 `NEXT_PUBLIC_BACKEND_BASE_URL` 与 `NEXT_PUBLIC_LANGGRAPH_BASE_URL` 未配置时的 fallback 行为

---

## Day 3：聊天页面主编排

### 阅读

- `frontend/src/app/workspace/chats/[thread_id]/page.tsx`
- `frontend/src/components/workspace/chats/use-thread-chat.ts`

### 实战

- 手绘聊天页组件结构图（header/message/input/todo/artifact）
- 跟踪 `new` -> 真实 thread id 的切换逻辑

### 验收

- 解释为什么这里使用 `history.replaceState` 而不是直接路由跳转

---

## Day 4：API 客户端与流式入口

### 阅读

- `frontend/src/core/api/api-client.ts`
- `frontend/src/core/api/stream-mode.ts`
- `frontend/src/core/threads/hooks.ts`（前半）

### 实战

- 跟踪 `getAPIClient()` 与 `useStream()` 参数
- 理解 stream mode 兼容层

### 验收

- 能说明为什么需要 `sanitizeRunStreamOptions`

---

## Day 5：深读 `useThreadStream`（核心）

### 阅读

- `frontend/src/core/threads/hooks.ts`（`useThreadStream` 全段）

### 实战

- 梳理一次发送完整链路：
  - optimistic
  - 上传
  - submit
  - 流式回调
  - finish

### 验收

- 能解释 `sendInFlightRef`、optimistic 清理时机、`onCustomEvent` 任务事件处理

---

## Day 6：线程 CRUD 与缓存更新

### 阅读

- `frontend/src/core/threads/hooks.ts`（`useThreads`、`useDeleteThread`、`useRenameThread`）
- `frontend/src/core/threads/types.ts`

### 实战

- 复刻简化线程列表 + 删除 + 重命名

### 验收

- 能正确使用 `setQueriesData` 与 `invalidateQueries`

---

## Day 7：设置系统与持久化

### 阅读

- `frontend/src/core/settings/local.ts`
- `frontend/src/core/settings/store.ts`
- `frontend/src/core/settings/hooks.ts`

### 实战

- 自己实现一版“全局设置 + 线程模型覆盖”存储模块

### 验收

- 刷新后设置保留
- 跨标签页设置同步成功

---

## Day 8：上传链路打通

### 阅读

- `frontend/src/core/uploads/api.ts`
- `frontend/src/core/uploads/index.ts`
- `frontend/src/core/threads/hooks.ts` 中上传相关逻辑

### 实战

- 复刻文件上传与消息附件显示

### 验收

- 上传后消息里能看到文件元信息（含 `virtual_path`）

---

## Day 9：模型与模式映射

### 阅读

- `frontend/src/core/models/api.ts`
- `frontend/src/core/models/hooks.ts`
- `frontend/src/core/threads/types.ts`

### 实战

- 做一个模式切换器，映射到 context：
  - flash/thinking/pro/ultra
  - thinking_enabled/is_plan_mode/subagent_enabled/reasoning_effort

### 验收

- 能输出并验证不同模式下传给后端的 context

---

## Day 10：i18n 与全局体验层

### 阅读

- `frontend/src/core/i18n/context.tsx`
- `frontend/src/core/i18n/server.ts`
- `frontend/src/app/layout.tsx`

### 实战

- 增加一个新翻译文案并在 UI 生效
- 验证 locale cookie 生效

### 验收

- 切换语言后页面文案变化且可持久化

---

## Day 11：认证骨架理解与复刻

### 阅读

- `frontend/src/server/better-auth/config.ts`
- `frontend/src/server/better-auth/server.ts`
- `frontend/src/app/api/auth/[...all]/route.ts`

### 实战

- 在练习项目搭一个同结构 auth route 与 session helper

### 验收

- 能说明当前认证接入范围和扩展点（provider、DB、权限）

---

## Day 12：Mock API 与离线演示

### 阅读

- `frontend/src/app/mock/api/models/route.ts`
- `frontend/src/app/mock/api/threads/search/route.ts`
- `frontend/src/app/mock/api/*`

### 实战

- 新增一个 mock endpoint（建议：memory 或 suggestions）

### 验收

- 后端关闭时，前端主要交互仍可演示

---

## Day 13：测试体系入门

### 阅读

- `frontend/vitest.config.ts`
- `frontend/playwright.config.ts`
- `frontend/tests/`（按本地实际展开）

### 实战

- 写 1 个 unit（如 stream mode sanitize）
- 写 1 个 e2e（新建会话并发送消息）

### 验收

- 单测与 E2E 至少各通过一个用例

---

## Day 14：总复刻（Mini DeerFlow Frontend）

### 实战目标

从空项目独立做出以下最小闭环：

- 聊天页
- 线程列表
- 流式响应
- 上传附件
- 模式切换
- 本地设置持久化

### 验收

- 不看源码可在 2~4 小时内搭出主链路
- 输出对比清单：与官方仓库差距、下一步优化点

---

## 每日执行模板（建议）

- 30%：读源码（记录关键设计）
- 60%：自己实现（避免直接复制）
- 10%：复盘（3 个收获 + 1 个疑问）

---

## 建议的本地验证命令

```bash
cd frontend
pnpm lint
pnpm typecheck
pnpm test
```

如需构建验证（按仓库常见要求设置 auth secret）：

```bash
cd frontend
$env:BETTER_AUTH_SECRET="local-dev-secret"
pnpm build
```

---

## 计划完成标准

完成 14 天后，你应具备：

1. 独立实现 AI Agent 前端主链路的能力
2. 理解流式会话与线程生命周期的工程模式
3. 具备复刻与扩展 DeerFlow Frontend 的基础工程能力
