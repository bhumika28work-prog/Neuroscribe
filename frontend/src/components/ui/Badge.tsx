import React from 'react';
import type { ReportStatus } from '../../types';

export interface BadgeProps {
  status: ReportStatus;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ status, className = '' }) => {
  const configs = {
    pending: {
      bg: 'bg-slate-100 border-slate-300 text-slate-800 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-300',
      text: 'Pending',
      dot: 'bg-slate-500',
    },
    processing: {
      bg: 'bg-amber-50 border-amber-200 text-amber-700 dark:bg-amber-500/10 dark:border-amber-500/20 dark:text-amber-400',
      text: 'Processing',
      dot: 'bg-amber-500 pulse-ring-active',
    },
    completed: {
      bg: 'bg-emerald-50 border-emerald-200 text-emerald-700 dark:bg-emerald-500/10 dark:border-emerald-500/20 dark:text-emerald-400',
      text: 'Completed',
      dot: 'bg-emerald-500',
    },
    failed: {
      bg: 'bg-rose-50 border-rose-200 text-rose-700 dark:bg-rose-500/10 dark:border-rose-500/20 dark:text-rose-400',
      text: 'Failed',
      dot: 'bg-rose-500',
    },
  };

  const current = configs[status] || configs.pending;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 text-[11px] font-bold rounded-full border shadow-sm transition-all duration-300 ${current.bg} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${current.dot}`} />
      <span>{current.text}</span>
    </span>
  );
};
