import { defineConfig, loadEnv } from 'vite'; // Import loadEnv to read env vars safely
import react from '@vitejs/plugin-react';
import path from 'path';

// We wrap this in a function to access 'mode' and env variables if needed
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@hooks': path.resolve(__dirname, './src/hooks'),
        '@store': path.resolve(__dirname, './src/store'),
        '@services': path.resolve(__dirname, './src/services'),
        '@utils': path.resolve(__dirname, './src/utils'),
        '@types': path.resolve(__dirname, './src/types'),
        '@config': path.resolve(__dirname, './src/config'),
      },
    },
    build: {
      target: 'es2022',
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true,
        },
      },
      rollupOptions: {
        output: {
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'ui-vendor': ['framer-motion', 'lucide-react'],
            'data-vendor': ['axios', '@tanstack/react-query', 'zustand'],
            'chart-vendor': ['recharts'],
          },
        },
      },
      chunkSizeWarningLimit: 500,
    },
    server: {
      host: true, // Required for Docker (binds to 0.0.0.0)
      port: 3000,
      
      // FIX 2: POLLING
      // This is REQUIRED for Docker to see your file changes on Mac/Windows
      watch: {
        usePolling: true,
        interval: 100,
      },

      // FIX 3: HMR Port Mapping
      // This ensures the browser knows to connect back to port 3000
      // even if the container internal IP changes.
      hmr: {
        clientPort: 3000, 
        // Note: If your 'emergent preview' URL stops working with HMR,
        // you might need to comment out 'clientPort' or make it conditional.
        // But for Localhost Docker, this is usually required.
      },

      allowedHosts: [
        'localhost',
        '4cc3583d-34e4-45c4-8925-cb018c0d93f1.preview.emergentagent.com',
        '.preview.emergentagent.com'
      ],
      proxy: {
        '/api': {
          // FIX 4: Dynamic Backend URL
          // In Docker, this must be 'http://backend:8001'
          // On Host, it is 'http://localhost:8001'
          target: env.VITE_BACKEND_URL || 'http://localhost:8001',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    optimizeDeps: {
      include: [
        'react', 
        'react-dom', 
        'zustand', 
        'axios',
        'react-syntax-highlighter',
        'react-syntax-highlighter/dist/cjs/styles/prism'
      ],
      esbuildOptions: {
        target: 'es2020',
      }
    },
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    },
  };
});