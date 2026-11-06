import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// The redesign mockups: a separate Vite root, never part of the app build (`npm run build` uses
// vite.config.ts and index.html only). Run with `npm run mockups`.
export default defineConfig({
  root: 'mockups',
  plugins: [react()],
  server: { host: '127.0.0.1', port: 5175 },
});
