import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Monolith Dark — Stitch 디자인 시스템
        "surface-dim": "#121315",
        "surface": "#121315",
        "surface-container-lowest": "#0d0e0f",
        "surface-container-low": "#1b1c1d",
        "surface-container": "#1f2021",
        "surface-container-high": "#292a2b",
        "surface-container-highest": "#343536",
        "surface-bright": "#38393a",
        "surface-variant": "#343536",
        "on-surface": "#e3e2e3",
        "on-surface-variant": "#c4c7c9",
        "outline": "#8e9194",
        "outline-variant": "#44474a",
        "primary": "#ffffff",
        "on-primary": "#2e3133",
        "primary-fixed": "#e1e3e6",
        "primary-fixed-dim": "#c4c7ca",
        "on-primary-fixed": "#191c1e",
        "secondary": "#c7c4d7",
        "on-secondary": "#2f2f3d",
        "secondary-container": "#464554",
        "on-secondary-container": "#b5b3c5",
        "inverse-surface": "#e3e2e3",
        "inverse-on-surface": "#303032",
        "inverse-primary": "#5c5f61",
        "error": "#ffb4ab",
        "error-container": "#93000a",
        "on-error": "#690005",
        "on-error-container": "#ffdad6",
        "on-tertiary-container": "#a64544",
        "background": "#121315",
        "on-background": "#e3e2e3",
        // Channel brand colors
        "ch-ga4": "#E37400",
        "ch-meta": "#1877F2",
        "ch-naver": "#03C75A",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        label: ["Space Grotesk", "sans-serif"],
        mono: ["Berkeley Mono", "JetBrains Mono", "monospace"],
      },
      borderRadius: {
        DEFAULT: "0.125rem",
        md: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
        full: "9999px",
      },
      animation: {
        "shimmer-slide": "shimmer-slide var(--speed) ease-in-out infinite alternate",
        "spin-around": "spin-around calc(var(--speed) * 2) infinite linear",
        "fade-in-up": "fade-in-up 0.55s ease-out forwards",
        "fade-in": "fade-in 0.4s ease-out forwards",
      },
      keyframes: {
        "shimmer-slide": {
          to: { transform: "translate(calc(100cqw - 100%), 0)" },
        },
        "spin-around": {
          "0%": { transform: "translateZ(0) rotate(0)" },
          "15%, 35%": { transform: "translateZ(0) rotate(90deg)" },
          "65%, 85%": { transform: "translateZ(0) rotate(270deg)" },
          "100%": { transform: "translateZ(0) rotate(360deg)" },
        },
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(24px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
