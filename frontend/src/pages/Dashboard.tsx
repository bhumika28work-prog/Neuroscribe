import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, Upload, FileText, Sparkles, Globe2, Clock } from 'lucide-react';
import { useReports, useDeleteReport } from '../hooks/useReports';
import { Button } from '../components/ui/Button';
import { Hero } from '../design/Hero';
import { StatCard } from '../design/StatCard';
import { ReportCard } from '../components/ui/ReportCard';
import { DashboardSkeleton } from '../components/ui/Skeleton';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const perPage = 9;

  const { data, isLoading, isError, error, refetch } = useReports(page, perPage);
  const deleteMutation = useDeleteReport();

  const handleDelete = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this medical report analysis?')) {
      try {
        await deleteMutation.mutateAsync(id);
        refetch();
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Failed to delete report.');
      }
    }
  };

  // Filter reports based on search query
  const filteredReports = data?.reports.filter((r) =>
    r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (r.original_filename && r.original_filename.toLowerCase().includes(searchQuery.toLowerCase()))
  ) || [];

  // Statistics calculations
  const totalReports = data?.total || 0;
  const analyzed = data?.reports.filter((r) => r.status === 'completed').length || 0;
  
  // Calculate relative time of the last uploaded report
  const getLastUploadText = () => {
    if (!data?.reports || data.reports.length === 0) return 'None';
    const sorted = [...data.reports].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
    const latestDate = new Date(sorted[0].created_at);
    const now = new Date();
    const diffMs = now.getTime() - latestDate.getTime();
    
    // Fallback for timezone or clock skew issues
    if (diffMs < 0) return 'Just now';
    
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return latestDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  return (
    <div className="space-y-10">
      {/* Hero Section */}
      <Hero
        title="AI-Powered Medical Report Analysis"
        subtitle="Upload reports, extract insights, and understand complex laboratory results in English and Hindi."
        ctaText="Analyze New Report"
        onCtaClick={() => navigate('/upload')}
        leftIcon={<Plus className="w-5 h-5" />}
      />

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard 
          title="Total Reports" 
          value={totalReports} 
          Icon={<FileText className="w-4 h-4" />}
        />
        <StatCard 
          title="AI Analyses" 
          value={analyzed} 
          trend="up" 
          subtext="Processed" 
          Icon={<Sparkles className="w-4 h-4" />}
        />
        <StatCard 
          title="Languages Supported" 
          value="2" 
          subtext="English & हिन्दी" 
          Icon={<Globe2 className="w-4 h-4" />}
        />
        <StatCard 
          title="Last Upload" 
          value={getLastUploadText()} 
          Icon={<Clock className="w-4 h-4" />}
        />
      </div>

      {/* Search Bar */}
      <div className="relative max-w-lg mx-auto w-full group">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-sky-600 transition-colors duration-200" />
        <input
          type="text"
          placeholder="Search reports..."
          className="w-full pl-11 pr-4 py-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800/80 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 text-slate-900 dark:text-slate-100 placeholder:text-slate-600 dark:placeholder:text-slate-500 shadow-sm transition-all duration-300"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Main Content */}
      {isLoading ? (
        <DashboardSkeleton />
      ) : isError ? (
        <div className="p-8 text-center border border-red-200/60 dark:border-red-900/40 bg-red-50/50 dark:bg-red-950/10 rounded-2xl max-w-md mx-auto">
          <h3 className="text-lg font-bold text-red-700 dark:text-red-400">Error Fetching Records</h3>
          <p className="mt-2 text-sm text-red-600 dark:text-red-300">
            {error instanceof Error ? error.message : 'Unknown network failure.'}
          </p>
          <Button variant="outline" className="mt-4" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      ) : filteredReports.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center max-w-md mx-auto border border-dashed border-slate-300 dark:border-slate-800 rounded-3xl p-8 bg-white dark:bg-slate-950/50 shadow-sm">
          <div className="flex items-center justify-center w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-500 mb-4">
            <Upload className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-extrabold text-slate-900 dark:text-slate-200">
            {searchQuery ? 'No matching reports' : 'No medical reports analyzed'}
          </h3>
          <p className="mt-2 text-sm text-slate-700 dark:text-slate-400 max-w-xs">
            {searchQuery
              ? 'Try searching with different keywords or identifiers.'
              : 'Upload a medical PDF report to begin generating structured AI summaries.'}
          </p>
          {!searchQuery && (
            <Button 
              variant="primary" 
              leftIcon={<Upload className="w-4 h-4" />} 
              onClick={() => navigate('/upload')} 
              className="mt-6"
            >
              Upload First PDF
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredReports.map((report) => (
            <ReportCard
              key={report.id}
              id={report.id}
              title={report.title}
              original_filename={report.original_filename}
              status={report.status}
              created_at={report.created_at}
              file_size_bytes={report.file_size_bytes}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total > perPage && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-200/60 dark:border-slate-800/60 pt-6 mt-8">
          <span className="text-xs sm:text-sm text-slate-700 dark:text-slate-400 font-medium">
            Showing <strong>{(page - 1) * perPage + 1}</strong> to <strong>{Math.min(page * perPage, data.total)}</strong> of <strong>{data.total}</strong> reports
          </span>
          <div className="flex gap-2 w-full sm:w-auto">
            <Button 
              variant="secondary" 
              size="sm" 
              disabled={page === 1} 
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              className="flex-1 sm:flex-none"
            >
              Previous
            </Button>
            <Button 
              variant="secondary" 
              size="sm" 
              disabled={page * perPage >= data.total} 
              onClick={() => setPage((p) => p + 1)}
              className="flex-1 sm:flex-none"
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
