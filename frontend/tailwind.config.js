/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    fontFamily: {
      sans: ['Vazirmatn', 'Tahoma', 'Segoe UI', 'system-ui', 'sans-serif'],
    },
    extend: {
      fontFamily: {
        vazir: ['Vazirmatn', 'Tahoma', 'Segoe UI', 'system-ui', 'sans-serif'],
      },
      colors: {
        surface: '#0d1018',
        surface2: '#161b25',
        surface3: '#1f2634',
        accent: '#4f8df6',
        accent2: '#6c63ff',
        border: '#2a3345',
        text: '#e8edf9',
        muted: '#8a99b8',
        success: '#2ec48a',
        warning: '#f5b35d',
        danger: '#ef5c69',
      },
      boxShadow: {
        soft: '0 18px 45px rgba(10, 14, 25, 0.22)',
        glow: '0 0 0 1px rgba(255,255,255,0.04), 0 20px 45px rgba(0,0,0,0.25)',
      },
      borderRadius: {
        xl: '1.25rem',
      },
      screens: {
        xs: '475px',
      },
    },
  },
  plugins: [],
};
