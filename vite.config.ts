import { defineConfig } from 'vite';

// SOVEREIGN//77 — Vite configuration.
// The engine layer (Three.js render loop + cinematic timeline) is intentionally
// kept out of React's reconciliation path; Vite only bundles it as plain modules.
//
// base: on `build` we target the GitHub Pages project subpath
// (https://ouomoxo.github.io/AFTER-EMELYN/); dev stays at root. Every runtime
// asset fetch is prefixed with import.meta.env.BASE_URL so it resolves correctly
// under the subpath regardless of the current (rewritten) URL.
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/AFTER-EMELYN/' : '/',
  resolve: {
    // Route bare `three` (incl. inside examples/jsm loaders) to the WebGPU build,
    // so the whole app shares ONE THREE copy. Without this, GLTFLoader would mint
    // core-`three` objects the WebGPURenderer can't recognize. `three/tsl` and
    // `three/examples/*` still resolve normally (regex only matches bare `three`).
    alias: [{ find: /^three$/, replacement: 'three/webgpu' }],
  },
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
}));
