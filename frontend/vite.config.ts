import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import * as path from 'path'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(process.cwd(), './src'), 
    },
  },
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: false,
        drop_debugger: true,
      },
    },
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': [
            'react', 
            'react-dom', 
            'react-router-dom',
            '@mantine/core',
            '@mantine/hooks',
            '@mantine/form',
            '@mantine/notifications',
            '@tanstack/react-query',
            'axios'
          ],
          'icons': ['@tabler/icons-react'],
        },
      },
    },
  },
  experimental: {
    renderBuiltUrl: (filename) => ({ relative: true }),
  },
  mode: 'development',
  logLevel: 'info',
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    },
    hmr: {
      timeout: 5000,
    },
    headers: {
      'Cache-Control': 'max-age=3600',
    },
    watch: {
      usePolling: false,
    },
  },
  css: {
    devSourcemap: true,
  },
  esbuild: {
    logOverride: { 'this-is-undefined-in-esm': 'silent' },
  },
  optimizeDeps: {
    include: [
      'react', 
      'react-dom', 
      'react-router-dom',
      '@mantine/core',
      '@mantine/hooks',
      '@mantine/form',
      '@mantine/notifications',
      '@tanstack/react-query',
      'axios',
      '@tabler/icons-react'
    ],
    force: false,
    esbuildOptions: {
      define: {
        global: 'globalThis',
      },
    },
  },
})
