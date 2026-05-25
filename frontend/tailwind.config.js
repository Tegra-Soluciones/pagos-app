/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#af282f",
          light:   "#fdf2f2",
          mid:     "#f5c5c7",
          dark:    "#8a1f25",
        },
      },
    },
  },
  plugins: [],
};
