import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { UploadReport } from './pages/UploadReport';
import ReportDetails from "./pages/ReportDetails";
import { NotFound } from "./pages/NotFound";
import { Reports } from "./pages/Reports";
import { Login } from "./pages/Login";
import { Signup } from "./pages/Signup";
// Add toast import
// import toast from 'react-hot-toast';

// Existing imports remain unchanged

import { Toaster } from 'react-hot-toast';

// Core React Query Client configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false, // Prevents aggressive background API updates during workspace navigation
      retry: 1,                    // Single retry on transient network failures
      staleTime: 30000,            // Consider data stale after 30 seconds
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Toaster />
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/upload" element={<UploadReport />} />
            <Route path="/reports/:id" element={<ReportDetails />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
