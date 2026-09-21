/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        // Backgrounds - from design_reference.json
        background: '#02070D',      // very dark navy/black
        panel: '#050D17',           // surface for panels
        card: '#07111E',            // card surface
        card_alt: '#091525',        // alternate card surface
        active: '#0B2550',          // active/selected state

        // Text colors
        primary: '#F3F7FF',       // primary text
        secondary: '#8FA3BB',     // secondary text
        muted: '#5D7188',         // muted text

        // Accent colors - BLUE FIRST as per design
        accent: {
          blue: '#1683FF',          // MAIN ACCENT COLOR
          blue_bright: '#2EA0FF',   // brighter blue for active states
          purple: '#8F5BFF',        // ONLY for secondary elements like PRACTICE
          yellow: '#FFC83D',        // for achievements, streaks, important accents
          green: '#16D69A',         // success, connected, sync
          red: '#FF5A6A',           // errors, destructive actions
        },

        // Border and effects
        border: 'rgba(40,110,170,0.35)', // 1px solid rgba(40,110,170,0.35)
      },

      borderWidth: {
        DEFAULT: '1px',
      },

      borderRadius: {
        DEFAULT: '8px',   // 8-10px radius
        lg: '10px',
      },

      spacing: {
        // Based on design reference measurements
        '22': '5.5rem',   // main offset/padding
        '18': '4.5rem',   // gap between sections
        '16': '4rem',     // content grid gap
        '11': '2.75rem',
        '10': '2.5rem',
        '9': '2.25rem',
        '8': '2rem',
        '7': '1.75rem',
        '6': '1.5rem',
        '5': '1.25rem',
        '4': '1rem',
        '3': '0.75rem',
        '2': '0.5rem',
        '1': '0.25rem',
        'sidebar': '230px',     // sidebar width from reference
        'header-height': '70px', // header height
        'main-left-offset': '230px', // offset for main content after sidebar
        'content-padding': '22px', // padding for main content area
        'gap': '18px',          // gap in main content area
        'content-grid-gap': '16px', // gap in content grid
      },

      fontFamily: {
        // Modern sans-serif as per design reference
        sans: ['system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        // Monospace/tabular numerals for numeric values
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
      },

      fontWeight: {
        // semibold/bold with restrained sizes
        semibold: '600',
        bold: '700',
      },

      // Transition duration
      transitionDuration: {
        DEFAULT: '180ms', // from design reference
      },

      // Box shadow - soft deep shadow, never oversized
      boxShadow: {
        sm: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08)',
        DEFAULT: '0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.08)',
        lg: '0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.08)',
        xl: '0 20px 25px rgba(0,0,0,0.1), 0 8px 10px rgba(0,0,0,0.08)',
        '2xl': '0 25px 50px rgba(0,0,0,0.15), 0 10px 20px rgba(0,0,0,0.08)',
        INNER: 'inset 0 2px 4px rgba(0,0,0,0.06)',
      },

      // Glow effects - subtle, localized
      dropShadow: {
        blue: '0 0 4px rgba(22, 131, 255, 0.3)',
        green: '0 0 4px rgba(22, 214, 154, 0.3)',
        yellow: '0 0 4px rgba(255, 200, 61, 0.3)',
        purple: '0 0 4px rgba(143, 91, 255, 0.3)',
      }
    },
  },
  plugins: [],
}