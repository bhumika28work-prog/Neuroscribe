import React from 'react';

export interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'rect' | 'circle';
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = '',
  variant = 'rect',
}) => {
  const variantStyles = {
    text: 'h-4 w-full rounded',
    rect: 'w-full rounded-xl',
    circle: 'rounded-full',
  };

  return (
    <div
      className={`shimmer-anim ${variantStyles[variant]} ${className}`}
      role="progressbar"
      aria-busy="true"
    />
  );
};

// Layout Skeletons for faster, cleaner visual building
export const DashboardSkeleton: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: 6 }).map((_, idx) => (
        <div key={idx} className="p-6 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <Skeleton className="w-20 h-5" />
            <Skeleton className="w-16 h-6 rounded-full" />
          </div>
          <Skeleton className="w-4/5 h-6 mt-2" />
          <div className="pt-4 border-t border-slate-50 flex items-center justify-between">
            <Skeleton className="w-24 h-4" />
            <Skeleton className="w-10 h-4" />
          </div>
        </div>
      ))}
    </div>
  );
};

export const DetailsSkeleton: React.FC = () => {
  return (
    <div className="space-y-8 animate-pulse">
      {/* Header Skeleton */}
      <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm space-y-3">
        <div className="flex items-center gap-3">
          <Skeleton className="w-10 h-10 rounded-xl" />
          <Skeleton className="w-48 h-8" />
          <Skeleton className="w-24 h-6 rounded-full ml-auto" />
        </div>
        <Skeleton className="w-64 h-4 ml-13" />
      </div>

      {/* Grid Content Skeletons */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm space-y-4">
          <Skeleton className="w-32 h-6" />
          <div className="space-y-2">
            <Skeleton className="h-4" />
            <Skeleton className="h-4" />
            <Skeleton className="h-4 w-5/6" />
          </div>
        </div>

        <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm space-y-4">
          <Skeleton className="w-32 h-6" />
          <div className="space-y-2">
            <Skeleton className="h-4" />
            <Skeleton className="h-4" />
            <Skeleton className="h-4 w-4/5" />
          </div>
        </div>
      </div>
    </div>
  );
};
