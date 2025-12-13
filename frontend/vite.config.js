import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/",
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
});
