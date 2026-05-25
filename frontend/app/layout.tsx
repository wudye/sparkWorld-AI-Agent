import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import "katex/dist/katex.min.css";
import { detectLocaleServer } from "@/core/i18n/server";
import { I18nProvider } from "@/core/i18n/context";
import { ThemeProvider } from "@/components/theme-provider";


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "recreate deerflow",
  description: "learn the harnees structure",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const local = await detectLocaleServer()
  return (
    <html
      lang={local}
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <ThemeProvider attribute="class">
          <I18nProvider initialLocale={local}>
            {children}
          </I18nProvider>
        </ThemeProvider>

      </body>
    </html>
  );
}
