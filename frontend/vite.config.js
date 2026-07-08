import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({

  plugins: [
    react(),
    tailwindcss(),
  ],

  server: {

    proxy: {

      "/api": {

        target:
          "https://by26l3ewyb.execute-api.us-east-1.amazonaws.com/Prod",

        changeOrigin: true,

        rewrite: (path) =>
          path.replace(/^\/api/, "")

      }

    }

  }

});