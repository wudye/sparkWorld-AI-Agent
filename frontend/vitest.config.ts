import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

import {resolve} from "path"
export default defineConfig({
    resolve: {
        alias: {
            '@': resolve(__dirname, './app'),
        },
        tsconfigPaths: true,
    },
    plugins: [ react()],
    test: {
        environment: 'jsdom',                    // 测试运行环境
        include: ["tests/unit/**/*.test.ts"],    // 测试文件匹配模式
        globals: true,                           // 全局 API 模式
        coverage: {                              // 代码覆盖率配置
            provider: "v8",                      // 使用 V8 引擎收集覆盖率
            reporter: ["text", "json", "html"],  // 输出格式
        },
    },

})