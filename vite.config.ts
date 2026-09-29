/* @index-begin
@index-end */
/** Development/build configuration. Symbols and variable locations: docs/code-index.md. */
import { defineConfig } from "vite";
export default defineConfig({
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
  build: { outDir: "dist", target: "es2022" },
});
