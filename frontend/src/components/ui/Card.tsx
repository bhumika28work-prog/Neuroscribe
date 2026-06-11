// src/components/ui/Card.tsx
import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, hoverable = false, className = '', ...props }) => {
  const baseStyles =
    'bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-850 rounded-2xl shadow-sm overflow-hidden transition-all duration-300';
  const hoverStyles = hoverable ? 'hover:shadow-lg hover:-translate-y-[1px] hover:border-slate-300 dark:hover:border-slate-800' : '';

  return (
    <div className={`${baseStyles} ${hoverStyles} ${className}`} {...props}>
      {children}
    </div>
  );
};
