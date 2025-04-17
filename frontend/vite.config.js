import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  // The root directory is implicitly 'frontend/' since vite.config.js is here.
  // We can be explicit if needed: root: '.',
  plugins: [
    react(), // Add the React plugin
  ],
  build: {
    // Output directory is 'dist' by default, relative to the root.
    // outDir: 'dist',
    // Sourcemaps can be enabled for debugging production builds
    // sourcemap: true,
  },
  server: { // Add server configuration
    proxy: {
      // Proxy /api requests to backend server running on port 5000
      '/api': {
        target: 'http://backend:5000', // Target the backend service in Docker
        changeOrigin: true, // Necessary for proxying
        // secure: false, // Keep commented unless needed
        rewrite: (path) => path.replace(/^\/api/, ''), // Remove /api prefix before forwarding
      }
    }
  },
  // Vite automatically uses postcss.config.js if present
  // css: {
  //   postcss: './postcss.config.js'
  // },
  // Public directory defaults to 'public' in the root
  // publicDir: 'public'
});