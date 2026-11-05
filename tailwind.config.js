/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/templates/**/*.html",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          50: '#fcf8eb',
          100: '#f8eed0',
          200: '#f0dca2',
          300: '#e7c66d',
          400: '#dcad3d',
          500: '#c9a84c',
          600: '#ad8733',
          700: '#866427',
          800: '#694e24',
          900: '#554020',
          accent: '#f0c040',
          light: '#ffd700',
        },
        dark: {
          950: '#050505',
          900: '#0a0a0a',
          850: '#101010',
          800: '#141414',
          700: '#1f1f1f',
          600: '#2a2a2a',
          500: '#3f3f3f',
        }
      },
      fontFamily: {
        heading: ['Poppins', 'sans-serif'],
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

