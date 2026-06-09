import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: {
          DEFAULT: "#0070f3", // Electric Blue
          foreground: "#ffffff",
        },
        secondary: {
          DEFAULT: "#1e293b", // Deep Dark Blue
          foreground: "#f8fafc",
        },
        accent: {
          DEFAULT: "#06b6d4", // Cyan
          foreground: "#083344",
        },
        muted: {
          DEFAULT: "#0f172a", // Midnight Blue
          foreground: "#94a3b8",
        },
        border: "rgba(255, 255, 255, 0.1)",
        card: {
          DEFAULT: "rgba(15, 23, 42, 0.6)", // Glassmorphism base
          foreground: "#f8fafc",
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "cyber-grid": "linear-gradient(rgba(0, 112, 243, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 112, 243, 0.1) 1px, transparent 1px)",
      },
      boxShadow: {
        "soft-glow": "0 0 15px rgba(0, 112, 243, 0.3)",
        "accent-glow": "0 0 20px rgba(6, 182, 212, 0.4)",
      },
    },
  },
  plugins: [],
}
export default config
