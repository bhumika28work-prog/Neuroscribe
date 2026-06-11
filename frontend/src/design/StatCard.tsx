// src/design/StatCard.tsx
import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

export interface StatCardProps {
  title: string;
  value: string | number;
  /** "up" for positive change, "down" for negative, undefined for neutral */
  trend?: 'up' | 'down';
  /** Optional subtext (e.g., % change) */
  subtext?: string;
  /** Optional icon component */
  Icon?: React.ReactNode;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  trend,
  subtext,
  Icon,
}) => {
  const trendColor =
    trend === 'up'
      ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10'
      : trend === 'down'
      ? 'text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-500/10'
      : 'text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800';

  const TrendIcon = trend === 'up' ? ArrowUpRight : trend === 'down' ? ArrowDownRight : null;

  return (
    <div className="premium-card p-6 flex flex-col justify-between h-full bg-white dark:bg-slate-900/40 backdrop-blur-md border border-slate-200/80 dark:border-slate-800/80 shadow-sm hover:shadow-lg transition-all duration-300">
      <div className="flex items-center justify-between gap-4">
        <span className="text-sm font-extrabold text-slate-700 dark:text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        {Icon && (
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-sky-50 dark:bg-sky-950/40 text-sky-500 dark:text-sky-400 border border-sky-100/50 dark:border-sky-900/30">
            {Icon}
          </div>
        )}
      </div>
      
      <div className="mt-4 flex items-baseline justify-between gap-2 flex-wrap">
        <span className="text-4xl font-heading font-black text-slate-900 dark:text-slate-50">
          {value}
        </span>
        {subtext && (
          <span className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-xs font-bold ${trendColor}`}>
            {TrendIcon && <TrendIcon className="w-3.5 h-3.5" />}
            <span>{subtext}</span>
          </span>
        )}
      </div>
    </div>
  );
};
