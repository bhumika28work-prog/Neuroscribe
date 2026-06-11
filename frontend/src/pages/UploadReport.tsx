import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, 
  FileText, 
  ArrowLeft, 
  CheckCircle, 
  AlertCircle, 
  ChevronRight,
  Brain,
  Loader
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useCreateReport, useUploadFile } from '../hooks/useReports';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

export const UploadReport: React.FC = () => {
  const navigate = useNavigate();
  
  // Wizard steps: 'metadata' | 'file' | 'processing' | 'success'
  const [step, setStep] = useState<'metadata' | 'file' | 'processing' | 'success'>('metadata');
  
  // State
  const [title, setTitle] = useState('');
  const [reportId, setReportId] = useState<number | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStatus, setProcessingStatus] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Mutations
  const createReportMutation = useCreateReport();
  const uploadFileMutation = useUploadFile();

  // Step 1: Submit Metadata
  const handleCreateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setErrorMsg(null);
    try {
      const report = await createReportMutation.mutateAsync({
        title: title.trim(),
        original_filename: selectedFile?.name || undefined,
      });
      toast.success('Report registered successfully');
      setReportId(report.id);
      setStep('file');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to register report.';
      toast.error(msg);
      setErrorMsg(msg);
    }
  };

  // Drag and Drop triggers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  // Client-side file type and size constraints
  const validateAndSetFile = (file: File) => {
    setErrorMsg(null);
    const extension = file.name.split('.').pop()?.toLowerCase();
    const validExtensions = ['pdf'];
    
    if (!extension || !validExtensions.includes(extension)) {
      setErrorMsg(`Unsupported file type: .${extension}. Only PDF files are allowed.`);
      return;
    }
    
    // 10 MB Limit
    if (file.size > 10 * 1024 * 1024) {
      setErrorMsg('File size exceeds the 10 MB maximum limit.');
      return;
    }

    setSelectedFile(file);
  };

  // Step 2: Upload File & Process
  const handleUpload = async () => {
    if (!selectedFile || reportId === null) return;

    setErrorMsg(null);
    setStep('processing');
    setUploadProgress(0);
    setProcessingStatus('Uploading medical document to server...');

    try {
      await uploadFileMutation.mutateAsync({
        reportId,
        file: selectedFile,
        onProgress: (pct) => {
          setUploadProgress(pct);
          if (pct === 100) {
            setProcessingStatus('PDF uploaded! Starting text extraction and AI medical summarization...');
          }
        },
      });
      toast.success('File uploaded and processing completed');
      setStep('success');
      
      setTimeout(() => {
        navigate(`/reports/${reportId}`);
      }, 1500);
      
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'File upload or extraction failed.';
      toast.error(msg);
      setErrorMsg(msg);
      setStep('file');
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="max-w-2xl mx-auto w-full py-6">
      {/* Back button */}
      <button
        onClick={() => {
          if (step === 'file') {
            setStep('metadata');
          } else {
            navigate('/');
          }
        }}
        className="inline-flex items-center gap-1.5 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200 text-sm font-semibold mb-6 transition-colors cursor-pointer"
        disabled={step === 'processing' || step === 'success'}
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back</span>
      </button>

      {/* Progress Wizard header */}
      <div className="flex items-center justify-between mb-8 px-4">
        <div className="flex items-center gap-2">
          <div className={`flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-all duration-300 ${
            step === 'metadata' ? 'bg-sky-500 text-white shadow-md shadow-sky-500/20' : 'bg-teal-500 text-white'
          }`}>
            1
          </div>
          <span className={`text-xs font-extrabold transition-colors ${step === 'metadata' ? 'text-sky-600 dark:text-sky-400' : 'text-slate-600'}`}>
            Configure Context
          </span>
        </div>
        
        <ChevronRight className="w-4 h-4 text-slate-500 dark:text-slate-700" />

        <div className="flex items-center gap-2">
          <div className={`flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-all duration-300 ${
            step === 'file' ? 'bg-sky-500 text-white shadow-md shadow-sky-500/20' : 
            step === 'processing' || step === 'success' ? 'bg-teal-500 text-white' : 'bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-400'
          }`}>
            2
          </div>
          <span className={`text-xs font-extrabold transition-colors ${step === 'file' || step === 'processing' ? 'text-sky-600 dark:text-sky-400' : 'text-slate-600'}`}>
            Upload Document
          </span>
        </div>
      </div>

      <Card className="p-8 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800/80 shadow-md">
        {/* Error notification block */}
        {errorMsg && (
          <div className="flex items-start gap-2.5 p-4 border border-rose-200 dark:border-rose-900/30 bg-rose-50/50 dark:bg-rose-950/10 rounded-xl text-rose-800 dark:text-rose-350 text-sm mb-6 animate-shake">
            <AlertCircle className="w-4.5 h-4.5 text-rose-500 flex-shrink-0 mt-0.5" />
            <span className="font-semibold leading-relaxed">{errorMsg}</span>
          </div>
        )}

        {/* STEP 1: Metadata setup */}
        {step === 'metadata' && (
          <form onSubmit={handleCreateReport} className="space-y-6">
            <div className="space-y-2">
              <h2 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-slate-100">
                Register Medical Report
              </h2>
              <p className="text-slate-700 dark:text-slate-450 text-sm leading-relaxed">
                Provide a context title for this diagnostic file. This helps index and locate clinical evaluations on your dashboard.
              </p>
            </div>

            <div className="space-y-2">
              <label htmlFor="title" className="text-xs font-bold text-slate-700 dark:text-slate-400 uppercase tracking-widest">
                Report Title
              </label>
              <input
                id="title"
                type="text"
                required
                autoFocus
                placeholder="e.g. Brain MRI - Rahul Sharma - June 2026"
                className="w-full px-4 py-3 border border-slate-300 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 bg-slate-50/50 dark:bg-slate-950/30 focus:bg-white dark:focus:bg-slate-950 transition-all text-slate-800 dark:text-slate-100 text-sm placeholder:text-slate-500"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                aria-label="Report title"
              />
              <p className="text-[11px] text-slate-600 dark:text-slate-500">Provide a clear title for identification.</p>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full py-3"
              isLoading={createReportMutation.isPending}
              rightIcon={<ChevronRight className="w-4 h-4" />}
              disabled={!title.trim() || createReportMutation.isPending}
              aria-label="Create report context"
            >
              {createReportMutation.isPending ? 'Creating...' : 'Continue'}
            </Button>
          </form>
        )}

        {/* STEP 2: File Upload Zone */}
        {step === 'file' && (
          <div className="space-y-6">
            <div className="space-y-2">
              <h2 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-slate-100">
                Upload Diagnostic File
              </h2>
              <p className="text-slate-700 dark:text-slate-450 text-sm leading-relaxed">
                Attach a PDF copy of the clinical diagnostics. The NLP compiler will parse, index, and summarize the patient charts.
              </p>
            </div>

            {/* Drag & drop visual block */}
            <div
              className={`relative border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center gap-3 transition-all cursor-pointer ${
                dragActive
                  ? 'border-sky-500 bg-sky-50/20 dark:bg-sky-950/10'
                  : selectedFile
                  ? 'border-emerald-500 bg-emerald-50/10 dark:bg-emerald-950/5'
                  : 'border-slate-300 dark:border-slate-800 hover:border-slate-400 dark:hover:border-slate-700 hover:bg-slate-50/50 dark:hover:bg-slate-900/20'
              }`}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={triggerFileInput}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".pdf"
                onChange={handleFileChange}
              />

              {selectedFile ? (
                <>
                  <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 dark:text-emerald-400 border border-emerald-100/50 dark:border-emerald-900/30 shadow-sm">
                    <FileText className="w-6 h-6 animate-pulse" />
                  </div>
                  <div className="text-center space-y-1">
                    <p className="text-sm font-bold text-slate-850 dark:text-slate-100 font-mono truncate max-w-sm">
                      {selectedFile.name}
                    </p>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFile(null);
                    }}
                    className="text-xs text-rose-500 dark:text-rose-450 hover:text-rose-700 font-bold hover:underline cursor-pointer"
                  >
                    Remove File
                  </button>
                </>
              ) : (
                <>
                  <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-sky-50 dark:bg-sky-950/30 text-sky-500 dark:text-sky-450 border border-sky-100/50 dark:border-sky-900/30 shadow-sm">
                    <Upload className="w-6 h-6" />
                  </div>
                  <div className="text-center space-y-1">
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      Drag & drop your diagnostic PDF report here
                    </p>
                    <p className="text-xs text-slate-600 dark:text-slate-500">
                      Only PDF documents are supported (Up to 10MB)
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="mt-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      triggerFileInput();
                    }}
                  >
                    Select File
                  </Button>
                </>
              )}
            </div>

            <div className="flex gap-4">
              <Button
                variant="secondary"
                className="flex-1 py-3"
                onClick={() => setStep('metadata')}
              >
                Back
              </Button>
              <Button
                variant="primary"
                className="flex-[2] py-3"
                disabled={!selectedFile}
                onClick={handleUpload}
              >
                Upload & Process
              </Button>
            </div>
          </div>
        )}

        {/* STEP 3: Uploading & Extraction processing loader */}
        {step === 'processing' && (
          <div className="flex flex-col items-center justify-center py-10 space-y-6">
            <div className="relative flex items-center justify-center">
              <div className="w-20 h-20 rounded-full border-4 border-slate-100 dark:border-slate-800 border-t-sky-500 animate-spin" />
              <Brain className="w-8 h-8 text-sky-500 absolute animate-pulse animate-duration-1000" />
            </div>

            <div className="text-center space-y-4 w-full">
              <h3 className="font-heading font-extrabold text-xl text-slate-800 dark:text-slate-100">
                Processing Document
              </h3>
              
              {/* Progress bar container */}
              <div className="max-w-md mx-auto w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden border border-slate-200/50 dark:border-slate-700/50 shadow-inner">
                <div 
                  className="bg-gradient-to-r from-sky-500 to-indigo-600 h-full rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              
              <div className="flex justify-between max-w-md mx-auto px-1 text-xs text-slate-700 dark:text-slate-500 font-bold font-mono">
                <span>Upload Progress</span>
                <span>{uploadProgress}%</span>
              </div>

              <p className="text-sm text-slate-700 dark:text-slate-400 font-semibold animate-pulse max-w-md mx-auto pt-2 leading-relaxed">
                {processingStatus}
              </p>
            </div>
          </div>
        )}

        {/* STEP 4: Success redirect message */}
        {step === 'success' && (
          <div className="flex flex-col items-center justify-center py-10 space-y-4">
            <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-50 dark:bg-emerald-950/30 text-emerald-500 dark:text-emerald-400 border border-emerald-100/50 dark:border-emerald-900/30 shadow-sm animate-bounce">
              <CheckCircle className="w-9 h-9" />
            </div>
            <h3 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-slate-150">
              Analysis Completed!
            </h3>
            <p className="text-slate-700 dark:text-slate-400 text-sm max-w-sm text-center leading-relaxed">
              Your clinical medical record has been successfully compiled. Launching visualization dashboard...
            </p>
            <Loader className="w-5 h-5 text-emerald-600 dark:text-emerald-400 animate-spin mt-4" />
          </div>
        )}
      </Card>
    </div>
  );
};
