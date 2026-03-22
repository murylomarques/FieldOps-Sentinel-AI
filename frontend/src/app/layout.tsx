import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "FIELDOPS SENTINEL AI",
  description: "Plataforma agentic de inteligencia operacional para equipes de campo.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}