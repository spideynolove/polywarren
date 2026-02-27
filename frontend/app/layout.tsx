import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "polywarren",
  description: "High-performance prediction market trading dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0a0a0a] text-[#ededed]">{children}</body>
    </html>
  );
}
