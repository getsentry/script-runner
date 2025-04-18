import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteStaticCopy } from "vite-plugin-static-copy";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    viteStaticCopy({
      targets: [
        {
          src: "node_modules/jq-web/jq.wasm",
          dest: "",
        },
      ],
    }),
  ],
  server: {
    proxy: {
      // Proxy API requests to Flask backend
      "/config": "http://127.0.0.1:5000",
      "/run": "http://127.0.0.1:5000",
      // Add any other backend API routes here
    },
  },
});
