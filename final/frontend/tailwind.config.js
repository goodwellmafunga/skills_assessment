/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#0E6B46',
          dark: '#0A5A3B',
          soft: 'rgba(14,107,70,0.12)',
        },

        background: '#F6F7F8',
        surface: '#FFFFFF',
        border: '#E7EAEE',

        text: {
          primary: '#101828',
          secondary: '#667085',
          tertiary: '#98A2B3',
        },

        success: '#12B76A',
        warning: '#F79009',
        neutral: '#D0D5DD',
      },

      borderRadius: {
        card: '16px',
        pill: '9999px',
      },

      boxShadow: {
        card: '0 10px 30px rgba(16,24,40,0.08)',
        cardHover: '0 14px 40px rgba(16,24,40,0.12)',
      },
    },
  },
  plugins: [],
}