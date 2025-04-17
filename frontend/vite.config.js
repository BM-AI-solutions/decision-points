import { defineConfig } from 'vite';
import legacy from '@vitejs/plugin-legacy';

export default defineConfig({
  // The root directory is implicitly 'frontend/' since vite.config.js is here.
  // We can be explicit if needed: root: '.',
  plugins: [
    legacy({
      targets: ['defaults', 'not IE 11'], // Adjust browser targets as needed
    }),
  ],
  build: {
    // Output directory is 'dist' by default, relative to the root.
    // outDir: 'dist',
    // Sourcemaps can be enabled for debugging production builds
    // sourcemap: true,
  },
  // Vite automatically uses postcss.config.js if present
  // css: {
  //   postcss: './postcss.config.js'
  // },
  // Public directory defaults to 'public' in the root
  // publicDir: 'public'
});