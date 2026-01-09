import type { Config } from "tailwindcss";

/**
 * Tailwind CSS configuration with responsive breakpoints
 * Task: T030, T204 [Phase 2, Phase 9]
 *
 * Breakpoints:
 * - sm: 640px (mobile landscape / large phones)
 * - md: 768px (tablets)
 * - lg: 1024px (small laptops / tablets landscape)
 * - xl: 1280px (desktops)
 * - 2xl: 1536px (large desktops)
 */
const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand colors for Promptly
        brand: {
          primary: "#6366f1", // Indigo
          secondary: "#8b5cf6", // Purple
          accent: "#06b6d4", // Cyan
          dark: "#0f172a", // Slate-900
          light: "#f1f5f9", // Slate-100
        },
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
      // Responsive container padding
      spacing: {
        "safe-top": "env(safe-area-inset-top)",
        "safe-bottom": "env(safe-area-inset-bottom)",
        "safe-left": "env(safe-area-inset-left)",
        "safe-right": "env(safe-area-inset-right)",
      },
      // Min heights for full-screen layouts
      minHeight: {
        "screen-safe": "calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom))",
      },
      // Animation for loading states
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "spin-slow": "spin 2s linear infinite",
        "fade-in": "fadeIn 0.3s ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
        "slide-down": "slideDown 0.3s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        slideDown: {
          "0%": { transform: "translateY(-10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
      // Typography scales for responsive text
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "0.875rem" }],
      },
      // Screen reader only utility
      screens: {
        xs: "475px",
        "3xl": "1920px",
      },
    },
  },
  plugins: [],
};

export default config;
