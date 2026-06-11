// src/design/tokens.ts

export const spacing = {
  xs: '0.5rem',
  sm: '0.75rem',
  md: '1rem',
  lg: '1.5rem',
  xl: '2rem',
  '2xl': '3rem',
};

export const radii = {
  none: '0px',
  sm: '0.375rem',
  md: '0.5rem',
  lg: '0.75rem',
  xl: '1rem',
  '2xl': '1.5rem',
  full: '9999px',
};

export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
};

export const colors = {
  // Brand colors mapping to Tailwind v4 theme variables
  primary: 'var(--color-primary)', 
  secondary: 'var(--color-indigo-brand)',
  success: 'var(--color-success)',
  warning: 'var(--color-warning)',
  error: 'var(--color-danger)',
  background: 'var(--color-bg-canvas)',
  card: 'var(--color-bg-card)',
};

export const gradients = {
  hero: 'bg-gradient-to-tr from-sky-500 via-blue-600 to-indigo-700',
  accent: 'bg-gradient-to-r from-sky-400 to-indigo-500',
  glass: 'bg-white/5 backdrop-blur-md',
};
