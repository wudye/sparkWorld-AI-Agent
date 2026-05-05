# Day 4-5: 前端基础与组件系统

**日期**: Day 4-5 (第四-五天)  
**目标**: 掌握 React 19 + TypeScript 开发，理解 Radix UI 组件库  
**预计时间**: 6-8 小时  
**难度**: ⭐⭐ (中等)  
**前置**: 完成 Day 1-3  

---

## 📋 学习概念

### 1. React 19 核心更新

**关键特性**（相比 React 18）:

1. **Server Components 默认**
   - 大幅减少客户端 JavaScript 体积
   - 直接访问后端资源
   - 改进的 SEO

2. **增强的表单处理**
   - `useFormStatus` Hook - 追踪表单提交状态
   - `useFormState` Hook - 管理 Server Action 的状态返回
   - 自动表单重置

3. **Hooks 改进**
   - `useContext` 更快
   - `useTransition` 改进
   - 新增 `useActionState`

4. **自动批处理**
   - 多个状态更新合并为单次渲染

### 2. TypeScript 在 React 中的应用

**类型安全的组件模式**:

```typescript
// Props 类型定义
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
}

// 带类型的函数式组件
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
  children,
}) => {
  return (
    <button 
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

// 使用时获得自动补全和类型检查
<Button variant="primary" size="lg" onClick={() => {}}>
  Click me
</Button>
```

### 3. Next.js 16 App Router

**文件系统路由**:
```
app/
├── layout.tsx          # 根布局 (所有页面适用)
├── page.tsx            # / 主页
├── about/
│   └── page.tsx        # /about
└── dashboard/
    ├── layout.tsx      # /dashboard 子布局
    └── page.tsx        # /dashboard
```

**关键概念**:
- **Server Components** (默认): 服务端渲染
- **Client Components**: `'use client'` 前缀
- **Layouts**: 嵌套布局+导航状态保留
- **Suspense**: 流式 SSR

### 4. Tailwind CSS v4

**核心特性**:
```css
/* 功能类 (Utility Classes) */
<div className="flex gap-4 px-6 py-4 bg-white rounded-lg shadow-sm">
  {/* flex: display: flex; gap: 1rem; ... */}
</div>

/* 响应式 */
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* 移动端 1 列，平板 2 列，桌面 3 列 */}
</div>

/* 暗黑模式 */
<div className="bg-white dark:bg-slate-900 text-black dark:text-white">
</div>
```

### 5. Radix UI - 无头组件

**特点**:
- 完全可访问性 (A11y)
- 无样式（自己控制 CSS）
- 与 Tailwind CSS 完美结合
- 提供原始 DOM 结构，供 Tailwind 样式化

**常用组件**:
- `Button` - 按钮
- `Dialog` - 对话框
- `Select` - 下拉选择
- `Input` - 输入框
- `Tabs` - 标签页
- `Tooltip` - 工具提示
- `Popover` - 弹出菜单

---

## 🛠️ Part 1: React 19 基础实践（Day 4 上午）

### 基础练习 1: 创建简单组件

创建文件 `frontend/src/components/basics/Counter.tsx`:

```typescript
'use client';

import { useState, useCallback } from 'react';

interface CounterProps {
  initialValue?: number;
  onChange?: (count: number) => void;
}

export const Counter: React.FC<CounterProps> = ({ 
  initialValue = 0,
  onChange 
}) => {
  const [count, setCount] = useState(initialValue);

  const handleIncrement = useCallback(() => {
    const newCount = count + 1;
    setCount(newCount);
    onChange?.(newCount);
  }, [count, onChange]);

  const handleDecrement = useCallback(() => {
    const newCount = count - 1;
    setCount(newCount);
    onChange?.(newCount);
  }, [count, onChange]);

  return (
    <div className="flex items-center gap-4">
      <button 
        onClick={handleDecrement}
        className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
      >
        -
      </button>
      <span className="text-2xl font-bold">{count}</span>
      <button 
        onClick={handleIncrement}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        +
      </button>
    </div>
  );
};

export default Counter;
```

**练习目标**:
- 理解 `useState` Hook
- 理解 `useCallback` 优化
- 理解 TypeScript Props 接口
- 理解 Tailwind 类名应用

### 基础练习 2: 了解 React 19 Server Actions

创建文件 `frontend/src/app/basics/actions.ts`:

```typescript
'use server';

export async function submitMessage(content: string) {
  // 这个函数运行在服务器上
  console.log('Received message:', content);
  
  // 可以直接访问数据库、API 等
  const result = await fetch('http://localhost:8001/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: content }),
  });

  return result.json();
}
```

创建文件 `frontend/src/components/basics/ServerActionForm.tsx`:

```typescript
'use client';

import { useActionState } from 'react';
import { submitMessage } from '@/app/basics/actions';

export const ServerActionForm = () => {
  const [state, formAction, isPending] = useActionState(submitMessage, null);

  return (
    <form action={formAction} className="space-y-4">
      <input
        type="text"
        name="content"
        placeholder="输入消息..."
        className="w-full px-4 py-2 border rounded"
        disabled={isPending}
      />
      <button
        type="submit"
        disabled={isPending}
        className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        {isPending ? '提交中...' : '提交'}
      </button>
      {state && <p className="text-green-600">结果: {JSON.stringify(state)}</p>}
    </form>
  );
};
```

**练习目标**:
- 理解 Server Actions
- 理解 `useActionState` Hook
- 理解表单状态追踪

---

## 🎨 Part 2: Radix UI 与组件库（Day 4 下午）

### Radix UI 练习 1: 按钮与对话框

创建文件 `frontend/src/components/radix/DialogExample.tsx`:

```typescript
'use client';

import * as Dialog from '@radix-ui/react-dialog';
import { useState } from 'react';

export const DialogExample = () => {
  const [open, setOpen] = useState(false);

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      {/* 触发按钮 */}
      <Dialog.Trigger asChild>
        <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
          打开对话框
        </button>
      </Dialog.Trigger>

      {/* 对话框背景（叠加层） */}
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50" />
        
        {/* 对话框内容 */}
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-96 space-y-4 bg-white p-6 rounded-lg shadow-lg">
          <Dialog.Title className="text-2xl font-bold">
            例子对话框
          </Dialog.Title>
          
          <Dialog.Description className="text-gray-600">
            这是一个 Radix UI 对话框示例。
          </Dialog.Description>

          <div className="space-y-4">
            <input
              type="text"
              placeholder="输入内容"
              className="w-full px-4 py-2 border rounded"
            />
          </div>

          <div className="flex justify-end gap-2">
            <Dialog.Close asChild>
              <button className="px-4 py-2 border rounded hover:bg-gray-100">
                取消
              </button>
            </Dialog.Close>
            <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
              确定
            </button>
          </div>

          {/* 关闭按钮 */}
          <Dialog.Close asChild>
            <button className="absolute right-4 top-4 text-gray-500 hover:text-gray-700">
              ✕
            </button>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};
```

**练习目标**:
- 理解 Radix UI 的组件分解（Trigger, Overlay, Content）
- 理解 `asChild` prop（传递 ref 给子元素）
- 理解通过 CSS 类自定义样式

### Radix UI 练习 2: 下拉选择

创建文件 `frontend/src/components/radix/SelectExample.tsx`:

```typescript
'use client';

import * as Select from '@radix-ui/react-select';
import { ChevronDownIcon } from '@radix-ui/react-icons';

export const SelectExample = () => {
  return (
    <Select.Root>
      <Select.Trigger className="flex items-center justify-between w-40 px-4 py-2 border rounded bg-white hover:bg-gray-50">
        <Select.Value placeholder="选择一个选项" />
        <Select.Icon>
          <ChevronDownIcon />
        </Select.Icon>
      </Select.Trigger>

      <Select.Portal>
        <Select.Content className="bg-white border rounded shadow-lg">
          <Select.Viewport className="p-2">
            <Select.Group>
              <Select.Label className="px-4 py-2 text-sm font-bold text-gray-700">
                第 1 组
              </Select.Label>
              
              {['选项 A', '选项 B', '选项 C'].map((option) => (
                <Select.Item
                  key={option}
                  value={option}
                  className="px-4 py-2 cursor-pointer hover:bg-blue-100"
                >
                  <Select.ItemText>{option}</Select.ItemText>
                </Select.Item>
              ))}
            </Select.Group>
          </Select.Viewport>
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  );
};
```

**练习目标**:
- 理解 Radix Select 的结构
- 理解 ItemText 与值的分离
- 理解受控组件状态

---

## 🏗️ Part 3: 项目文件结构理解（Day 5 上午）

### 3.1 查看现有组件库

```powershell
# 查看前端组件结构
cd F:\qbot\deer-flow-main\deer-flow-main\frontend
Get-ChildItem -Recurse src/components | Select-Object Name, FullName | Format-Table
```

**预期结构**:
```
src/components/
├── chat/              # 聊天相关
│   ├── ChatWindow.tsx
│   └── MessageList.tsx
├── layout/            # 布局组件
│   ├── Header.tsx
│   └── Sidebar.tsx
├── models/            # 模型选择相关
├── ui/                # 通用 UI 组件
│   ├── Button.tsx
│   ├── Input.tsx
│   └── Dialog.tsx
└── ...
```

### 3.2 分析现有按钮组件

```powershell
# 打开并分析
code src/components/ui/Button.tsx
# 或
notepad src/components/ui/Button.tsx
```

**学习要点**:
- 如何组织 TypeScript Props 接口
- 如何使用 Radix UI 原始组件
- 如何用 Tailwind 应用样式
- 如何处理变体（variants）

### 3.3 查看 App Router 结构

```powershell
# 查看路由
Get-ChildItem -Recurse src/app | Select-Object Name, FullName
```

**理解**:
- 每个 `page.tsx` 对应一个路由
- `layout.tsx` 的嵌套
- `loading.tsx` 和 `error.tsx` 的用途

---

## 🔄 Part 4: 组件复用与设计系统（Day 5 下午）

### 设计系统练习：创建统一的主题

创建文件 `frontend/src/core/theme/constants.ts`:

```typescript
export const COLORS = {
  primary: '#3b82f6',      // 蓝色
  secondary: '#8b5cf6',    // 紫色
  success: '#10b981',      // 绿色
  danger: '#ef4444',       // 红色
  warning: '#f59e0b',      // 橙色
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    500: '#6b7280',
    900: '#111827',
  },
};

export const SIZES = {
  xs: '0.75rem',   // 12px
  sm: '0.875rem',  // 14px
  base: '1rem',    // 16px
  lg: '1.125rem',  // 18px
  xl: '1.25rem',   // 20px
};

export const SPACING = {
  0: '0',
  1: '0.25rem',
  2: '0.5rem',
  3: '0.75rem',
  4: '1rem',
  6: '1.5rem',
  8: '2rem',
};

export const BORDER_RADIUS = {
  sm: '0.25rem',
  base: '0.375rem',
  lg: '0.5rem',
  full: '9999px',
};
```

### 创建可复用的按钮组件

创建文件 `frontend/src/components/ui/Button.tsx`:

```typescript
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/core/utils/cn';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed',
  {
    variants: {
      variant: {
        primary: 'bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-500',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
        danger: 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-500',
        ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
      },
      size: {
        sm: 'px-3 py-1 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
      },
      rounded: {
        sm: 'rounded-sm',
        md: 'rounded-md',
        full: 'rounded-full',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      rounded: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant, 
    size, 
    rounded, 
    isLoading,
    icon,
    children,
    ...props 
  }, ref) => (
    <button
      className={cn(buttonVariants({ variant, size, rounded, className }))}
      disabled={isLoading || props.disabled}
      ref={ref}
      {...props}
    >
      {isLoading && <span className="animate-spin">⏳</span>}
      {icon && <span>{icon}</span>}
      {children}
    </button>
  )
);

Button.displayName = 'Button';
```

**关键概念**:
- **CVA (class-variance-authority)**: 类型安全的变体管理
- **forwardRef**: 暴露 DOM ref，用于父组件控制
- **displayName**: 调试时显示组件名

### 创建实用函数 `cn`

创建文件 `frontend/src/core/utils/cn.ts`:

```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * 合并 Tailwind CSS 类名，解决冲突
 * @example
 * cn('px-2 py-1', 'px-4') => 'py-1 px-4'  // px-4 覆盖 px-2
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

**安装依赖**:
```powershell
cd frontend
pnpm add clsx tailwind-merge class-variance-authority
```

---

## ✅ 实战检查清单

### Day 4 上午检查

- [ ] 创建了 `Counter.tsx` 组件并能本地预览
- [ ] 理解了 `useState` 和 `useCallback`
- [ ] 理解了 TypeScript Props 接口
- [ ] 测试了 Tailwind 类名应用

### Day 4 下午检查

- [ ] 创建了 `DialogExample.tsx`
- [ ] 创建了 `SelectExample.tsx`
- [ ] 能解释 Radix UI 的组件分解模式
- [ ] 能说出 asChild prop 的作用

### Day 5 上午检查

- [ ] 查看了现有的组件库文件
- [ ] 分析了至少 2 个现有组件
- [ ] 理解了 App Router 的路由映射

### Day 5 下午检查

- [ ] 创建了主题常量文件
- [ ] 实现了通用 Button 组件（支持变体）
- [ ] 创建了 `cn` 工具函数
- [ ] 理解了 CVA 库的用途

---

## 📚 学习资源

| 资源 | 链接 | 预计时间 |
|------|------|---------|
| React 19 官方文档 | https://react.dev | 30 min |
| TypeScript in React | https://react-typescript-cheatsheet.netlify.app | 20 min |
| Next.js 16 App Router | https://nextjs.org/docs/app | 20 min |
| Tailwind CSS 文档 | https://tailwindcss.com/docs | 15 min |
| Radix UI 文档 | https://www.radix-ui.com/docs/primitives | 30 min |
| CVA 库入门 | https://cva.style | 10 min |

---

## 🎯 Day 4-5 目标总结

完成后应该能够：

✅ 使用 React Hooks（useState, useCallback, useContext）  
✅ 编写类型安全的 TypeScript React 组件  
✅ 理解 Next.js 16 App Router 与 Server Components  
✅ 使用 Tailwind CSS 进行样式设计  
✅ 理解 Radix UI 无头组件架构  
✅ 构建一个有变体的组件系统  
✅ 掌握组件复用和设计系统最佳实践  

---

## ⏱️ 时间记录

| 阶段 | 预计时间 | 实际时间 |
|------|---------|---------|
| Part 1: React 基础 (Day 4 AM) | 2 小时 | ___ |
| Part 2: Radix UI (Day 4 PM) | 2 小时 | ___ |
| Part 3: 项目结构 (Day 5 AM) | 1.5 小时 | ___ |
| Part 4: 设计系统 (Day 5 PM) | 2.5 小时 | ___ |
| **总计** | **6-8 小时** | **___** |

---

**下一步**: 完成后，进入 Day 6 - 页面布局与 UI 库集成

