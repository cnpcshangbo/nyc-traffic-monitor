import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  assetsInclude: ['**/*.mp4'],
  base: process.env.NODE_ENV === 'production' ? '/nyc-traffic-monitor/' : '/',
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
