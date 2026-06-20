import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base must match the GitHub Pages subpath: https://nogor-design.github.io/workflow-mri/
// Override with VITE_BASE for other hosts (e.g. "/" for a custom domain).
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE ?? "/workflow-mri/",
  build: { outDir: "dist" },
});
