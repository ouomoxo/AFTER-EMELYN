import { defineConfig } from 'vite';

// SOVEREIGN//77 — Vite configuration.
// The engine layer (Three.js render loop + cinematic timeline) is intentionally
// kept out of React's reconciliation path; Vite only bundles it as plain modules.
export default defineConfig({
  base: './',
  server: {
    host: true,
    port: 5173,
  },
  build: {
    target: 'esnext',
    assetsInlineLimit: 0, // never inline .glb / .ktx2 — they stream per scene
    rollupOptions: {
      output: {
        manualChunks: {
          three: ['three'],
        },
      },
    },
  },
  worker: {
    format: 'es',
  },
});
