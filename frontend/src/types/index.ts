export type ReportStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Report {
  id: number;
  title: string;
  original_filename: string | null;
  status: ReportStatus;
  file_type: string | null;
  file_size_bytes: number | null;
  file_path: string | null;
  extracted_text: string | null;
  ai_summary: string | null;
  hindi_summary: string | null;
  patient_explanation: string | null;
  hindi_explanation: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface ReportListResponse {
  total: number;
  page: number;
  per_page: number;
  reports: Report[];
}

export interface UploadSuccessResponse {
  success: boolean;
  message: string;
  file_name: string;
  original_name: string;
  file_path: string;
  file_size_bytes: number;
  file_type: string;
  report_id: number;
}

export interface CreateReportPayload {
  title: string;
  original_filename?: string;
}

export interface APIErrorResponse {
  success: boolean;
  error: string;
  detail?: string;
}
