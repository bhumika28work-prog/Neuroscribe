import React from 'react';

export type ButtonProps = {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  className?: string;
  disabled?: boolean;
};

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  leftIcon,
  rightIcon,
  className = '',
  disabled = false,
}) => {
  const base = 'inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl font-semibold transition-all duration-300 focus:outline-none disabled:opacity-50 disabled:pointer-events-none active:scale-[0.97]';
  const variants = {
    primary: 'bg-gradient-to-tr from-sky-500 to-indigo-600 hover:shadow-lg hover:shadow-sky-500/10 text-white hover:brightness-105',
    secondary: 'bg-white hover:bg-slate-50 text-slate-800 border border-slate-200 shadow-sm dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-100 dark:border-slate-700',
    outline: 'border border-sky-300 text-sky-600 hover:bg-sky-50 dark:border-sky-800 dark:text-sky-400 dark:hover:bg-sky-950/20',
  };
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant]} ${className}`}
    >
      {leftIcon && <span className="w-4 h-4 flex items-center justify-center">{leftIcon}</span>}
      <span>{children}</span>
      {rightIcon && <span className="w-4 h-4 flex items-center justify-center">{rightIcon}</span>}
    </button>
  );
};
