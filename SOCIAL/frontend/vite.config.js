// import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react'

// export default defineConfig({
//   plugins: [react()],
//   server: {
//     host: true,
//     port: 5173
//   },
//   preview: {
//     host: '0.0.0.0',
//     port: process.env.PORT || 4173,
//     allowedHosts: [
//       'frontend-agentic.onrender.com',
//       '.onrender.com',
//       'localhost',
//       '127.0.0.1'
//     ]
//   },
//   build: {
//     outDir: 'dist',
//     sourcemap: false,
//     rollupOptions: {
//       output: {
//         manualChunks: undefined
//       }
//     }
//   },
//   define: {
//     global: 'globalThis'
//   }
// })


import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'   // ✅ ADD THIS

export default defineConfig({
  plugins: [react()],

  resolve: {              // ✅ ADD THIS BLOCK
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  server: {
    host: true,
    port: 5173
  },

  preview: {
    host: '0.0.0.0',
    port: process.env.PORT || 4173,
    allowedHosts: [
      'frontend-agentic.onrender.com',
      '.onrender.com',
      'localhost',
      '127.0.0.1'
    ]
  },

  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  },

  define: {
    global: 'globalThis'
  }
})
