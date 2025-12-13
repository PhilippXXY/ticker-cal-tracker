import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  // Use the repository path when building for production so assets resolve on GitHub Pages
  base: mode === "production" ? "/ticker-cal-tracker/" : "/",
  build: {
    outDir: "dist",
  },
  server: {
    proxy: {
      "/api": {
        target: "https://ticker-cal-tracker-1052233055044.europe-west2.run.app",
        changeOrigin: true,
        secure: true,
      },
    },
  },
}));
