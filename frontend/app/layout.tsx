import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Crucible Eval",
  description: "Generate runnable eval suites for LLM apps",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
