/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)',
        'bg-grouped': 'var(--bg-grouped)',
        surface: 'var(--surface)',
        'surface-glass': 'var(--surface-glass)',
        text: 'var(--text)',
        'text-2': 'var(--text-2)',
        'text-3': 'var(--text-3)',
        accent: 'var(--accent)',
        'accent-hover': 'var(--accent-hover)',
        'accent-solid': 'var(--accent-solid)',
        'accent-solid-hover': 'var(--accent-solid-hover)',
        hairline: 'var(--hairline)',
        focus: 'var(--focus)',
        'viz-forecast': 'var(--viz-forecast)',
        'viz-actual': 'var(--viz-actual)',
        'viz-conservative': 'var(--viz-conservative)',
        'viz-over': 'var(--viz-over)',
        'viz-under': 'var(--viz-under)',
        'viz-vintage': 'var(--viz-vintage)',
        'viz-purple': 'var(--viz-purple)',
        'viz-teal': 'var(--viz-teal)',
        'viz-pink': 'var(--viz-pink)',
        'viz-indigo': 'var(--viz-indigo)',
      },
      borderRadius: {
        card: 'var(--r-card)',
        control: 'var(--r-control)',
        pill: 'var(--r-pill)',
        chip: 'var(--r-chip)',
      },
      boxShadow: {
        1: 'var(--shadow-1)',
        2: 'var(--shadow-2)',
        glass: 'var(--shadow-glass)',
      },
      fontFamily: {
        sans: ['var(--font)'],
      },
    },
  },
  plugins: [],
}
