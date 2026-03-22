import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#f6f8fc",
        foreground: "#0f172a",
        primary: "#0a4da2",
        secondary: "#0f766e",
        accent: "#f59e0b",
        surface: "#ffffff",
        ink: "#1f2937"
      },
      fontFamily: {
        sans: ["Manrope", "ui-sans-serif", "system-ui"],
        display: ["Sora", "ui-sans-serif", "system-ui"]
      },
      boxShadow: {
        panel: "0 10px 30px -12px rgba(2, 6, 23, 0.18)"
      }
    }
  },
  plugins: []
};

export default config;


