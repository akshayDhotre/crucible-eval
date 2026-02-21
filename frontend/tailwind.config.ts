import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0e1116",
        mist: "#f4f7fb",
        accent: "#c95f2e",
        slate: "#304058",
      },
    },
  },
  plugins: [],
};

export default config;
