import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "FIELDOPS SENTINEL AI",
  description: "An agentic operations intelligence platform for field service teams.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
