# Day 6: 页面布局与 UI 库集成

**日期**: Day 6 (第六天)  
**目标**: 构建应用主框架，集成主要 UI 组件  
**预计时间**: 5-6 小时  
**难度**: ⭐⭐ (中等)  
**前置**: 完成 Day 4-5  

---

## 📋 学习概念

### 1. Next.js 布局系统

**关键概念**:
- **Root Layout**: `app/layout.tsx` - 应用顶级布局
- **Nested Layouts**: 子路由的共享布局
- **Layout 不重新渲染**: 导航时仅更新 page，不重新渲染 layout
- **Parallel Routes**: 多个独立的路由分支

### 2. DeerFlow UI 架构

**预期布局**:
```
┌─────────────────────────────────────┐
│         Header / Navigation         │
├─────────────┬───────────────────────┤
│  Sidebar    │                       │
│  (左侧)     │   Main Content Area   │
│            │                       │
│  - 模型     │   - 聊天窗口          │
│  - 技能     │   - 消息列表          │
│  - 设置     │   - 输入框            │
│            │   - 工件展示          │
└─────────────┴───────────────────────┘
```

### 3. Radix UI 集合集成

**常用组件**:
- **Tabs**: 标签页切换
- **Accordion**: 折叠菜单
- **Popover**: 弹出菜单
- **Tooltip**: 悬停提示
- **Separator**: 分隔符

### 4. 响应式设计

**断点**:
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

**Tailwind 响应式类**:
```
sm:  640px   md: 768px   lg: 1024px   xl: 1280px   2xl: 1536px
```

---

## 🛠️ Part 1: 根布局构建（2 小时）

### 步骤 1.1: 创建全局样式

编辑 `frontend/src/app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 全局样式 */
body {
  @apply bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-50;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-800;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-400 dark:bg-gray-600 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-600 dark:bg-gray-400;
}

/* 代码块美化 */
code {
  @apply bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm;
  font-family: 'Monaco', 'Courier New', monospace;
}

pre {
  @apply bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto;
}
```

### 步骤 1.2: 创建根布局

编辑 `frontend/src/app/layout.tsx`:

```typescript
import type { Metadata, Viewport } from 'next';
import { Providers } from '@/app/providers';
import './globals.css';

export const metadata: Metadata = {
  title: 'DeerFlow - 超级代理平台',
  description: 'LangGraph + Next.js 构建的智能代理应用',
  viewport: 'width=device-width, initial-scale=1',
};

export const viewport: Viewport = {
  colorScheme: 'light dark',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh" suppressHydrationWarning>
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
```

### 步骤 1.3: 创建 Providers 组件

创建 `frontend/src/app/providers.tsx`:

```typescript
'use client';

import { ReactNode } from 'react';
import { ThemeProvider } from 'next-themes';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/core/api/queryClient';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="light">
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </ThemeProvider>
  );
}
```

**安装依赖**:
```powershell
cd frontend
pnpm add next-themes @tanstack/react-query
```

---

## 🖼️ Part 2: 主布局组件（2 小时）

### 步骤 2.1: 创建主布局

创建 `frontend/src/app/(dashboard)/layout.tsx`:

```typescript
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
      {/* 顶部头部 */}
      <Header />
      
      {/* 主容器（头部下方） */}
      <div className="flex flex-1 overflow-hidden">
        {/* 左侧边栏 */}
        <aside className="hidden sm:block w-64 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 overflow-y-auto">
          <Sidebar />
        </aside>

        {/* 主内容区域 */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
```

### 步骤 2.2: 创建 Header 组件

创建 `frontend/src/components/layout/Header.tsx`:

```typescript
'use client';

import { Menu, Moon, Sun, LogOut } from 'lucide-react';
import { useTheme } from 'next-themes';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuSeparator,
  DropdownMenuItem,
} from '@/components/ui/DropdownMenu';

export function Header() {
  const { theme, setTheme } = useTheme();

  return (
    <header className="sticky top-0 z-40 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
        {/* Logo 和标题 */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg" />
          <h1 className="text-xl font-bold hidden sm:block">DeerFlow</h1>
        </div>

        {/* 右侧操作 */}
        <div className="flex items-center gap-2">
          {/* 主题切换 */}
          <button
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
          >
            {theme === 'light' ? (
              <Moon className="w-5 h-5" />
            ) : (
              <Sun className="w-5 h-5" />
            )}
          </button>

          {/* 用户菜单 */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition">
                <Menu className="w-5 h-5" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>设置</DropdownMenuItem>
              <DropdownMenuItem>帮助</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <LogOut className="w-4 h-4 mr-2" />
                退出登录
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
```

### 步骤 2.3: 创建 Sidebar 组件

创建 `frontend/src/components/layout/Sidebar.tsx`:

```typescript
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  MessageCircle,
  Settings,
  Zap,
  FileText,
  ChevronDown,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from '@/components/ui/Accordion';

const menuItems = [
  {
    label: '新建对话',
    href: '/chat',
    icon: MessageCircle,
  },
];

const sidebarSections = [
  {
    label: '功能',
    items: [
      { label: '技能库', icon: Zap, href: '/skills' },
      { label: '文档', icon: FileText, href: '/docs' },
      { label: '设置', icon: Settings, href: '/settings' },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState(false);

  const isActive = (href: string) => pathname.startsWith(href);

  return (
    <div className="flex flex-col h-full">
      {/* 新建按钮 */}
      <div className="p-4">
        <Button variant="primary" size="md" className="w-full">
          <MessageCircle className="w-4 h-4" />
          新建对话
        </Button>
      </div>

      {/* 分隔符 */}
      <div className="border-t border-gray-200 dark:border-gray-800" />

      {/* 侧边栏菜单 */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        <Accordion type="single" collapsible>
          {sidebarSections.map((section) => (
            <AccordionItem key={section.label} value={section.label}>
              <AccordionTrigger className="hover:no-underline">
                <span className="font-medium text-sm">{section.label}</span>
              </AccordionTrigger>
              <AccordionContent className="space-y-1 pb-0">
                {section.items.map((item) => {
                  const isItemActive = isActive(item.href);
                  return (
                    <Link key={item.href} href={item.href}>
                      <div
                        className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition ${
                          isItemActive
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100 font-medium'
                            : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                        }`}
                      >
                        <item.icon className="w-4 h-4" />
                        <span>{item.label}</span>
                      </div>
                    </Link>
                  );
                })}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </nav>

      {/* 底部信息 */}
      <div className="border-t border-gray-200 dark:border-gray-800 p-4">
        <p className="text-xs text-gray-500 dark:text-gray-600">
          DeerFlow v1.0.0
        </p>
      </div>
    </div>
  );
}
```

**注意**: 需要创建 Accordion 和 DropdownMenu 组件或使用 Radix UI

---

## 🎨 Part 3: Radix UI 组件集成（1 小时）

### 创建 Accordion 组件

创建 `frontend/src/components/ui/Accordion.tsx`:

```typescript
'use client';

import * as AccordionPrimitive from '@radix-ui/react-accordion';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/core/utils/cn';

export const Accordion = AccordionPrimitive.Root;

export const AccordionItem = AccordionPrimitive.Item;

export const AccordionTrigger = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitive.Trigger>
>(({ className, children, ...props }, ref) => (
  <AccordionPrimitive.Header className="flex">
    <AccordionPrimitive.Trigger
      ref={ref}
      className={cn(
        'flex flex-1 items-center justify-between py-2 px-3 font-medium text-sm transition-all hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg [&[data-state=open]>svg]:rotate-180',
        className
      )}
      {...props}
    >
      {children}
      <ChevronDown className="h-4 w-4 transition-transform duration-200" />
    </AccordionPrimitive.Trigger>
  </AccordionPrimitive.Header>
));

export const AccordionContent = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <AccordionPrimitive.Content
    ref={ref}
    className={cn('overflow-hidden text-sm px-3 py-1', className)}
    {...props}
  >
    <div className="space-y-1">{children}</div>
  </AccordionPrimitive.Content>
));
```

### 创建 DropdownMenu 组件

创建 `frontend/src/components/ui/DropdownMenu.tsx`:

```typescript
'use client';

import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu';
import { cn } from '@/core/utils/cn';

export const DropdownMenu = DropdownMenuPrimitive.Root;
export const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger;

export const DropdownMenuContent = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Content>
>(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.Portal>
    <DropdownMenuPrimitive.Content
      ref={ref}
      className={cn(
        'min-w-[200px] bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg shadow-lg p-1 z-50',
        className
      )}
      {...props}
    />
  </DropdownMenuPrimitive.Portal>
));

export const DropdownMenuItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Item>
>(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.Item
    ref={ref}
    className={cn(
      'flex items-center px-3 py-2 text-sm rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none',
      className
    )}
    {...props}
  />
));

export const DropdownMenuSeparator = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Separator>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Separator>
>(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.Separator
    ref={ref}
    className={cn('my-1 -mx-1 h-px bg-gray-200 dark:bg-gray-800', className)}
    {...props}
  />
));
```

---

## ✅ 实战检查清单

- [ ] 创建了根布局和页面结构✓  
- [ ] Header 组件正确显示✓  
- [ ] Sidebar 组件正确显示✓  
- [ ] 主题切换功能可用✓  
- [ ] Accordion 和 DropdownMenu 集成完成✓  
- [ ] 在浏览器中验证了布局✓  
- [ ] 响应式设计在移动端能正常工作✓  

---

## ⏱️ 时间记录

| 任务 | 预计时间 | 实际时间 |
|------|---------|---------|
| Part 1: 根布局构建 | 2 小时 | ___ |
| Part 2: 主布局组件 | 2 小时 | ___ |
| Part 3: Radix UI 集成 | 1 小时 | ___ |
| **总计** | **5-6 小时** | **___** |

---

**下一步**: 完成后，进入 Day 7-9 - 前端集成与实时通信

