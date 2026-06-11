import React from 'react';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  label,
  className = '',
}) => {
  const sizes = {
    sm: 'w-5 h-5 border-2',
    md: 'w-10 h-10 border-3',
    lg: 'w-16 h-16 border-4',
  };

  return (
    <div className={`flex flex-col items-center justify-center space-y-4 ${className}`} role="status">
      <div
        className={`animate-spin rounded-full border-slate-100 border-t-sky-500 border-r-transparent border-b-sky-500 border-l-transparent ${sizes[size]}`}
      />
      {label && (
        <p className="text-sm font-semibold text-slate-500 animate-pulse text-center">
          {label}
        </p>
      )}
    </div>
  );
};
export default LoadingSpinner;
