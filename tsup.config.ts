import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["cjs", "esm"],
  minify: true,
  sourcemap: false,
  splitting: false,
  clean: true,
  dts: true,
  esbuildOptions(options) {
    options.loader = {
      ...options.loader,
      '.py': 'text'  // 将 .py 文件作为文本加载
    };
  }
});