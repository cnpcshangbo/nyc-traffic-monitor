import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  assetsInclude: ['**/*.mp4'],
  server: {
    host: '0.0.0.0',  // Allow external connections
    port: 5173,
    allowedHosts: [
      'classification.boshang.online',
      'localhost',
      '127.0.0.1'
    ]
  }
})
