import { defineConfig } from 'vitest/config';

// Unit tests for pure frontend logic (`npm test`). Kept apart from vite.config.ts so the app build
// is untouched. No browser: anything that needs one is checked by hand or by a lab script.
export default defineConfig({
  test: {
    include: ['src/**/*.test.ts'],
    environment: 'node',
  },
});
