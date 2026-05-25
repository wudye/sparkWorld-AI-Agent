export const SUPPORTED_LOCALES = ["en-US", "zh-CN"] as const;
export type Locale = (typeof SUPPORTED_LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "en-US";

export function isLocale(value: string) : value is Locale {
    return (SUPPORTED_LOCALES as readonly string[]).includes(value);
}


export function getLocaleByLang(lang: string): Locale {
    const normalizedLang = lang.toLowerCase();
    for (const locale of SUPPORTED_LOCALES) {
        if (locale.startsWith(normalizedLang)) {
            return locale;
        }
    }
    return DEFAULT_LOCALE;

}


export function getLangByLocale(locale: Locale): string {
    const parts = locale.split("-");
    if (parts.length > 0 && typeof parts[0] === "string") {
        return parts[0];
    }
    return locale;
}


export function normalizeLocale(locale: string | null | undefined): Locale {
  if (!locale) {
    return DEFAULT_LOCALE;
  }

  if (isLocale(locale)) {
    return locale;
  }

  if (locale.toLowerCase().startsWith("zh")) {
    return "zh-CN";
  }

  return DEFAULT_LOCALE;
}


  /*
  服务端环境检测 - 如果 window 不存在，
  说明代码在服务器端运行（如 SSR/SSG）
  获取浏览器语言：- navigator.language：
  现代浏览器的首选语言（如 "zh-CN"）-
   navigator.userLanguage：IE 浏览器的兼容写法
  */
export function detectLocale(): Locale {

  if (typeof window === "undefined") {
    return DEFAULT_LOCALE;
  }

  const browserLang =
    navigator.language ||
    (navigator as unknown as { userLanguage: string }).userLanguage;

  return normalizeLocale(browserLang);
}
