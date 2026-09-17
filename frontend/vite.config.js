import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["apple-touch-icon.png"],
      manifest: {
        name: "Set Together",
        short_name: "SetTogether",
        description: "Log workouts, follow friends, share PRs.",
        start_url: "/",
        scope: "/",
        display: "standalone",
        // Matches the app's own dark concrete background / accent colors.
        background_color: "#1c1b19",
        theme_color: "#1c1b19",
        icons: [
          { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
          { src: "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
        ],
      },
      workbox: {
        // Don't cache API responses or video files - only the app shell
        // itself, so data always stays fresh while the app still loads
        // instantly and works offline for navigation.
        globPatterns: ["**/*.{js,css,html,ico,png,svg}"],
      },
    }),
  ],
  server: { port: 5173 },
});
