import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Calendar, FileText, Trash2, ArrowRight } from 'lucide-react';

export interface ReportCardProps {
  id: number;
  title: string;
  original_filename?: string | null;
  status: string;
  created_at: string;
  file_size_bytes: number | null;
  onDelete: (e: React.MouseEvent, id: number) => void;
}

export const ReportCard: React.FC<ReportCardProps> = ({
  id,
  title,
  original_filename,
  status,
  created_at,
  file_size_bytes,
  onDelete,
}) => {
  const navigate = useNavigate();

  const formatBytes = (bytes: number | null): string => {
    if (bytes === null || bytes === undefined) return 'N/A';
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    try {
      return new Date(dateString).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return 'N/A';
    }
  };

  // Border color based on status
  const getStatusBorder = () => {
    if (status === 'completed') return 'border-l-4 border-l-emerald-500';
    if (status === 'failed') return 'border-l-4 border-l-rose-500';
    if (status === 'processing') return 'border-l-4 border-l-amber-500';
    return 'border-l-4 border-l-slate-400';
  };

  return (
    <Card 
      hoverable 
      className={`flex flex-col h-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800/80 shadow-md transition-all duration-300 hover:shadow-xl hover:scale-[1.01] ${getStatusBorder()}`}
    >
      <div 
        className="p-6 flex-1 flex flex-col justify-between space-y-4" 
        onClick={() => navigate(`/reports/${id}`)}
      >
        {/* Header: ID & Badge */}
        <div className="flex items-center justify-between gap-4">
          <span className="text-[10px] font-bold text-slate-600 dark:text-slate-500 uppercase tracking-widest">
            ID: #{id}
          </span>
          <Badge status={status as any} />
        </div>

        {/* Report Information */}
        <div className="space-y-2">
          <h3 className="font-heading font-extrabold text-base text-slate-800 dark:text-slate-100 line-clamp-2 hover:text-sky-600 dark:hover:text-sky-400 transition-colors">
            {title}
          </h3>
          <div className="flex items-center gap-1.5 text-xs text-slate-700 dark:text-slate-400 font-mono truncate max-w-full">
            <FileText className="w-3.5 h-3.5 flex-shrink-0 text-slate-500" />
            <span className="truncate">{original_filename || 'No file attached'}</span>
          </div>
        </div>

        {/* Date and Size */}
        <div className="pt-4 border-t border-slate-200 dark:border-slate-800/60 flex items-center justify-between text-xs text-slate-700 dark:text-slate-400 font-medium">
          <div className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-slate-500 dark:text-slate-500" />
            <span>{formatDate(created_at)}</span>
          </div>
          <span>{formatBytes(file_size_bytes)}</span>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="px-6 py-3 bg-slate-50/50 dark:bg-slate-900/30 border-t border-slate-200 dark:border-slate-800/60 flex items-center justify-between">
        <Button 
          variant="ghost" 
          size="sm"
          className="text-xs text-sky-600 dark:text-sky-400 font-bold flex items-center gap-1 hover:text-sky-700 dark:hover:text-sky-300 p-0 hover:bg-transparent" 
          onClick={() => navigate(`/reports/${id}`)}
        >
          View Analysis <ArrowRight className="w-3 h-3 transition-transform group-hover:translate-x-0.5" />
        </Button>
        <button
          className="p-1.5 text-slate-500 hover:text-rose-600 dark:text-slate-500 dark:hover:text-rose-400 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/20 transition-all cursor-pointer active:scale-90"
          onClick={(e) => onDelete(e, id)}
          title="Delete report"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </Card>
  );
};
