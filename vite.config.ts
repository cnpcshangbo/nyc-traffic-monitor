import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// Determine base path based on environment variable or deployment target
// - For GitHub Pages: '/UMDL2/' or '/nyc-traffic-monitor/'
// - For FRP/Docker: '/'
const base = process.env.VITE_BASE_PATH || '/'

function cspPlugin(command: 'serve' | 'build') {
  const isDev = command === 'serve'
  const content = isDev
    ? "script-src 'self' 'unsafe-eval' 'unsafe-inline' https: data: blob:; style-src 'self' 'unsafe-inline' https: data:; img-src 'self' data: https: blob:; connect-src 'self' https: http: wss: ws:; media-src 'self' https: http: data: blob:; default-src 'self' https:;"
    : "script-src 'self' 'unsafe-inline' https: data:; style-src 'self' 'unsafe-inline' https: data:; img-src 'self' data: https:; connect-src 'self' https: http: wss: ws:; media-src 'self' https: http: data: blob:; default-src 'self' https:;"

  return {
    name: 'html-csp-inject',
    transformIndexHtml() {
      return [
        {
          tag: 'meta',
          inject: 'head',
          attrs: {
            'http-equiv': 'Content-Security-Policy',
            content,
          },
        },
      ]
    },
  }
}

export default defineConfig(({ command }) => ({
  plugins: [react(), cspPlugin(command)],
  assetsInclude: ['**/*.mp4'],
  base,
  server: {
    host: '0.0.0.0', // Allow external connections
    port: 5173,
    allowedHosts: [
      'classification.boshang.online',
      'asdfghjklzxcvbnm.aimobilitylab.xyz',
      'localhost',
      '127.0.0.1',
    ],
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
  },
  build: {
    minify: true,
    sourcemap: false,
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts', // For @testing-library/jest-dom
    globals: true,
  },
}))
