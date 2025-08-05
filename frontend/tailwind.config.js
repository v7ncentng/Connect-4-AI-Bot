/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // These paths tell Tailwind which files to scan for CSS classes
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}