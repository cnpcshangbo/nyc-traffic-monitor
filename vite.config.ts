import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// Determine base path based on environment variable or deployment target
// - For GitHub Pages: '/UMDL2/' or '/nyc-traffic-monitor/'
// - For FRP/Docker: '/'
const base = process.env.VITE_BASE_PATH || '/';

export default defineConfig({
  plugins: [react()],
  assetsInclude: ['**/*.mp4'],
  base: base,
  server: {
    host: '0.0.0.0',  // Allow external connections
    port: 5173,
    allowedHosts: [
      'classification.boshang.online',
      'asdfghjklzxcvbnm.aimobilitylab.xyz',
      'localhost',
      '127.0.0.1'
    ]
  },
  preview: {
    host: '0.0.0.0',
    port: 5173
  },
  build: {
    // Optimize for production
    minify: true,
    sourcemap: false
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts', // For @testing-library/jest-dom
    globals: true,
  }
})
