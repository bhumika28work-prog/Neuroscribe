import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { 
  Report, 
  ReportListResponse, 
  CreateReportPayload, 
  UploadSuccessResponse 
} from '../types';

// Query Key factory for consistent cache tagging
export const reportKeys = {
  all: ['reports'] as const,
  lists: () => [...reportKeys.all, 'list'] as const,
  list: (page: number, perPage: number) => [...reportKeys.lists(), { page, perPage }] as const,
  details: () => [...reportKeys.all, 'detail'] as const,
  detail: (id: number) => [...reportKeys.details(), id] as const,
};

// 1. Fetch paginated reports
export function useReports(page: number, perPage: number) {
  return useQuery({
    queryKey: reportKeys.list(page, perPage),
    queryFn: async () => {
      const response = await apiClient.get<ReportListResponse>('/reports', {
        params: { page, per_page: perPage },
      });
      return response.data;
    },
    placeholderData: (previousData) => previousData, // keep previous page data while loading
  });
}

// 2. Fetch single report details (with intelligent background polling)
export function useReportDetails(reportId: number) {
  return useQuery({
    queryKey: reportKeys.detail(reportId),
    queryFn: async () => {
      const response = await apiClient.get<Report>(`/reports/${reportId}`);
      return response.data;
    },
    // Poll the server every 3 seconds only if the report status is 'pending' or 'processing'
    refetchInterval: (query) => {
      const report = query.state.data;
      if (report && (report.status === 'pending' || report.status === 'processing')) {
        return 3000;
      }
      return false;
    },
    refetchIntervalInBackground: true,
  });
}

// 3. Mutation: Create report record
export function useCreateReport() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (payload: CreateReportPayload) => {
      const response = await apiClient.post<Report>('/reports', payload);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate report lists to fetch the fresh report
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() });
    },
  });
}

// 4. Mutation: Upload file with progress tracking
export function useUploadFile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      reportId,
      file,
      onProgress,
    }: {
      reportId: number;
      file: File;
      onProgress?: (percentage: number) => void;
    }) => {
      const formData = new FormData();
      formData.append('report_id', String(reportId));
      formData.append('file', file);

      const response = await apiClient.post<UploadSuccessResponse>('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total && onProgress) {
            const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(percentage);
          }
        },
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate the specific report detail cache and lists
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reportKeys.detail(data.report_id) });
    },
  });
}

// 5. Mutation: On-demand AI Summarization
export function useSummarizeReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (reportId: number) => {
      const response = await apiClient.post<Report>(`/reports/${reportId}/summarize`);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reportKeys.detail(data.id) });
    },
  });
}

// 6. Mutation: Delete report
export function useDeleteReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (reportId: number) => {
      const response = await apiClient.delete<{ success: boolean; message: string }>(
        `/reports/${reportId}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() });
    },
  });
}
