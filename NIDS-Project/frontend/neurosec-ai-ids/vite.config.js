import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: '/',
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        login: resolve(__dirname, 'login.html')
      },
      output: {
        manualChunks: {
          echarts: ['echarts']
        }
      }
    }
  },
  css: {
    preprocessorOptions: {
      css: {
        charset: false
      }
    }
  }
});