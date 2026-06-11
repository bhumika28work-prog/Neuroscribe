import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useReports } from '../hooks/useReports';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Table, TableHeader, TableBody, TableRow, TableCell, TableHead } from '../components/ui/Table';
import { Loader2 } from 'lucide-react';

export const Reports: React.FC = () => {
  const navigate = useNavigate();
  const page = 1;
  const perPage = 20;
  const { data, isLoading, isError, error } = useReports(page, perPage);

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return 'N/A';
    }
  };

  return (
    <Card className="p-6">
      <h1 className="font-heading text-2xl font-bold text-slate-900 mb-4">All Reports</h1>
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin w-8 h-8 text-sky-600" />
        </div>
      )}
      {isError && (
        <div className="text-center py-12 text-red-600">
          <p>{error instanceof Error ? error.message : 'Failed to load reports.'}</p>
          <Button variant="outline" className="mt-4" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      )}
      {(!isLoading && !isError && data && data.reports.length === 0) && (
        <div className="text-center py-12 text-slate-600">
          <p>No reports found.</p>
        </div>
      )}
      {data && data.reports.length > 0 && (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-1/3">Title</TableHead>
                <TableHead className="w-1/6">Status</TableHead>
                <TableHead className="w-1/4">Created</TableHead>
                <TableHead className="w-1/6 text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.reports.map((report) => (
                <TableRow key={report.id} className="hover:bg-slate-50 cursor-pointer" onClick={() => navigate(`/reports/${report.id}`)}>
                  <TableCell className="font-medium text-slate-800">{report.title}</TableCell>
                  <TableCell>
                    <Badge status={report.status} />
                  </TableCell>
                  <TableCell>{formatDate(report.created_at)}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); navigate(`/reports/${report.id}`); }}>
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </Card>
  );
};
