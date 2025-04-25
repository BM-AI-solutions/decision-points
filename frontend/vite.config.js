import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import postcssImport from 'postcss-import';
import autoprefixer from 'autoprefixer';
import tailwindcss from 'tailwindcss'; // Import tailwindcss
import cssnano from 'cssnano';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const isProd = mode === 'production';

  return {
    plugins: [
      react(),
    ],
    build: {
      // Optimize build for performance
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: isProd, // Remove console logs in production
          drop_debugger: true,
          pure_funcs: isProd ? ['console.log', 'console.debug', 'console.info'] : []
        }
      },
      // Reduce chunk size
      chunkSizeWarningLimit: 1000,
      // Optimize CSS
      cssCodeSplit: true,
      // Generate source maps for easier debugging
      sourcemap: !isProd,
      // Rollup specific options
      rollupOptions: {
        output: {
          // Optimize asset organization
          assetFileNames: (assetInfo) => {
            let extType = assetInfo.name.split('.').at(1);
            if (/\.css$/.test(assetInfo.name)) {
              extType = 'css';
            } else if (/\.(png|jpe?g|gif|svg|webp)$/.test(assetInfo.name)) {
              extType = 'images';
            } else if (/\.(woff2?|ttf|eot)$/.test(assetInfo.name)) {
              extType = 'fonts';
            }
            return `assets/${extType}/[name]-[hash][extname]`;
          },
          // Optimize code splitting
          manualChunks: (id) => {
            if (id.includes('node_modules')) {
              if (id.includes('react') || id.includes('react-dom')) {
                return 'vendor-react';
              }
              if (id.includes('chart.js') || id.includes('react-chartjs-2')) {
                return 'vendor-chart';
              }
              if (id.includes('socket.io')) {
                return 'vendor-socketio';
              }
              return 'vendor'; // all other packages
            }
          }
        }
      }
    },
    server: {
      port: 3000,
      hmr: {
        overlay: true,
      },
      proxy: {
        '/api/v1': {
          target: 'http://backend:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/v1/, '/api/v1')
        }
      }
    },
    // Optimize dependency pre-bundling
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        'chart.js',
        'react-chartjs-2',
        'socket.io-client'
      ],
      esbuildOptions: {
        target: 'es2020'
      }
    },
    // CSS optimization
    css: {
      devSourcemap: false,
      modules: {
        // Generate more readable class names in development
        generateScopedName: isProd ? '[hash:base64:8]' : '[name]__[local]'
      },
      postcss: {
        plugins: [
          postcssImport(), // Process @import rules
          tailwindcss(), // Add Tailwind CSS
          autoprefixer(), // Add vendor prefixes
          isProd && cssnano({
            preset: ['advanced', {
              discardComments: { removeAll: true },
              reduceIdents: false,
              zindex: false,
              colormin: true,
              convertValues: true
            }]
          })
        ].filter(Boolean)
      }
    },
    // Performance optimizations
    esbuild: {
      logOverride: { 'this-is-undefined-in-esm': 'silent' },
      target: 'es2020',
      // Optimize tree-shaking
      treeShaking: true
    }
  };
});