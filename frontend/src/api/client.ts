import axios, { AxiosError } from 'axios';
import type { APIErrorResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000, // 45 seconds (handling synchronous OCR + AI summarization delays)
});

// Interceptor to extract clean error messages from backend responses
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<APIErrorResponse>) => {
    let errorMessage = 'An unexpected error occurred. Please try again.';

    if (error.response) {
      // The server responded with a status code outside the 2xx range
      const errorData = error.response.data;
      
      if (typeof errorData === 'object' && errorData !== null) {
        if (errorData.error) {
          errorMessage = errorData.error;
        } else if (errorData.detail) {
          // FastAPI standard ValidationErrors detail is sometimes an array or a string
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            errorMessage = (errorData.detail as any[])
              .map((err: any) => `${err.loc.join('.')}: ${err.msg}`)
              .join(', ');
          }
        }
      }
    } else if (error.request) {
      // The request was made but no response was received
      errorMessage = 'Unable to connect to the medical server. Please check your network connection.';
    } else {
      // Something happened in setting up the request
      errorMessage = error.message;
    }

    return Promise.reject(new Error(errorMessage));
  }
);
