import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /**
   * Additional Tailwind classes applied to the input element.
   */
  className?: string;
}

/**
 * A styled input component consistent with the design system used across the app.
 * It forwards all native input attributes and merges them with a base Tailwind style.
 */
export const Input: React.FC<InputProps> = ({ className = '', ...props }) => {
  const baseStyles = 'w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500/30 focus:border-sky-500 bg-slate-50/50 focus:bg-white transition-all text-slate-800 text-sm placeholder:text-slate-500';
  return <input className={`${baseStyles} ${className}`} {...props} />;
};

export default Input;
