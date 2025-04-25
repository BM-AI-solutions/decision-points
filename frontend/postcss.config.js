module.exports = {
  plugins: [
    // Import CSS files - process imports first
    require('postcss-import'),

    // Add Tailwind CSS
    require('tailwindcss'),

    // Add autoprefixer for better browser compatibility
    require('autoprefixer'),

    // Only run PurgeCSS in production to remove unused CSS
    process.env.NODE_ENV === 'production' && require('@fullhuman/postcss-purgecss')({
      content: [
        './index.html',
        './src/**/*.{js,jsx,ts,tsx}'
      ],
      defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || [],
      safelist: [
        /body/,
        /html/,
        /^btn/,
        /^modal/,
        /^dashboard/,
        /^nav/,
        /^hero/,
        /^feature/,
        /^pricing/,
        /^testimonial/,
        /^container/,
        /^animate/,
        /^fade/,
        /^fa-/,
        /^fas /
      ],
      // Reduce CSS size more aggressively
      rejected: true
    }),

    // Optimize CSS with cssnano - run after PurgeCSS
    require('cssnano')({
      preset: ['default', {
        discardComments: { removeAll: true },
        normalizeWhitespace: true,
        colormin: true,
        minifyFontValues: true,
        minifySelectors: true,
        // Disable potentially risky optimizations
        reduceIdents: false,
        zindex: false,
        mergeIdents: false
      }]
    })
  ].filter(Boolean)
};