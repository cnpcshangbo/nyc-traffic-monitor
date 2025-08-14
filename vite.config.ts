import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// Determine base path based on environment variable or default to repo name
// For fork: change to '/UMDL2/' or your repository name
const base = process.env.VITE_BASE_PATH || '/UMDL2/';

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
  }
})
