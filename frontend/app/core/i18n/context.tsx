"use client"

import { createContext, useContext, useState, type ReactNode } from "react";

import type { Locale } from "@/core/i18n";

/* 全局语言状态管理器" —— 让应用的所有组件都能读取和修改当前语言，并且自动保存到 Cookie 实现持久化。 */

export interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
}


export const I18nContext = createContext<I18nContextType | null>(null);

export function I18nProvider({
    children,
    initialLocale,}: {
    children: ReactNode;
    initialLocale: Locale;
}) {
    const [locale, setLocale] = useState<Locale>(initialLocale);

    const handleSetLocale = (newLocale: Locale) => {
        setLocale(newLocale);
        document.cookie = `locale=${newLocale}; path=/; max-age=31536000`;
    }
    return (
        <I18nContext.Provider value={{ locale, setLocale: handleSetLocale }}>
            {children}
        </I18nContext.Provider>     
    )
}

export function useI18nContext() {
    const context = useContext(I18nContext);
    if (!context) {
        throw new Error("useI18nContext must be used within a I18nProvider");
    }
    return context;
}