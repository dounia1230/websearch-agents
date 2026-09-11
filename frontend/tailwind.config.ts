import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "#d8dee8",
        input: "#d8dee8",
        ring: "#1d4ed8",
        background: "#eef3f8",
        foreground: "#0f172a",
        primary: {
          DEFAULT: "#153e75",
          foreground: "#f8fbff",
        },
        secondary: {
          DEFAULT: "#e6eef8",
          foreground: "#16314f",
        },
        muted: {
          DEFAULT: "#edf2f7",
          foreground: "#526071",
        },
        accent: {
          DEFAULT: "#dbeafe",
          foreground: "#12396f",
        },
        card: {
          DEFAULT: "#ffffff",
          foreground: "#0f172a",
        },
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem",
        "3xl": "2rem",
      },
      boxShadow: {
        panel: "0 20px 45px -28px rgba(15, 23, 42, 0.28)",
        soft: "0 10px 25px -18px rgba(21, 62, 117, 0.35)",
      },
      fontFamily: {
        sans: ["Manrope", "ui-sans-serif", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      backgroundImage: {
        "mesh-blue":
          "radial-gradient(circle at top left, rgba(59, 130, 246, 0.22), transparent 34%), radial-gradient(circle at top right, rgba(29, 78, 216, 0.18), transparent 26%), linear-gradient(180deg, #f6f8fb 0%, #eef3f8 100%)",
      },
    },
  },
  plugins: [],
};

export default config;
