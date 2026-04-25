/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef4ff',
          100: '#dae6ff',
          500: '#3b6df0',
          600: '#2f57d4',
          700: '#2645aa',
        },
      },
    },
  },
  plugins: [],
};
