import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import Icons from "unplugin-icons/vite";
import path from "path";

export default defineConfig({
  plugins: [
    vue(),
    Icons({ compiler: "vue3", autoInstall: true }),
  ],

  base: "/assets/pagos/pagos/",

  build: {
    outDir: path.resolve(__dirname, "../pagos/public/pagos"),
    emptyOutDir: true,
    target: "es2015",
    rollupOptions: {
      output: {
        entryFileNames: "main.js",
        chunkFileNames: "[name]-[hash].js",
        assetFileNames: (info) =>
          info.name === "index.css" ? "index.css" : "[name]-[hash].[ext]",
      },
    },
  },

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },

  server: {
    port: 8081,
    proxy: {
      "^/(api|assets|files|private|app)": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
        ws: true,
      },
    },
  },

  optimizeDeps: {
    include: ["frappe-ui > @popperjs/core"],
  },
});
