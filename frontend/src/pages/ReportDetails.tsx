import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  BrainCircuit,
  FileText,
  Sparkles,
  RefreshCw,
  Copy, Download,
  Check,
  Calendar,
  Shield,
  FileCode,
  HardDrive,
  AlertCircle
} from 'lucide-react';
import { useReportDetails, useSummarizeReport } from '../hooks/useReports';
import toast from 'react-hot-toast';
import { jsPDF } from 'jspdf';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { DetailsSkeleton } from '../components/ui/Skeleton';

export default function ReportDetails() {
  const { id } = useParams<{ id: string }>();
  const reportId = Number(id);
  const navigate = useNavigate();

  // Tabs: 'insights' | 'text' | 'specs'
  const [activeTab, setActiveTab] = useState<'insights' | 'text' | 'specs'>('insights');
  const [copied, setCopied] = useState(false);
  const [copiedSummary, setCopiedSummary] = useState(false);
  const [copiedExplanation, setCopiedExplanation] = useState(false);
  const [language, setLanguage] = useState<'en' | 'hi'>('en');
  const [summaryLanguage, setSummaryLanguage] = useState<'en' | 'hi'>('en');

  // Queries
  const { data: report, isLoading, isError, error } = useReportDetails(reportId);
  const summarizeMutation = useSummarizeReport();

  // Check if AI Summary or Patient Explanation is missing
  const isSummaryMissing = report ? (!report.ai_summary || !report.patient_explanation) : false;

  // Handle re-trigger AI summarization
  const handleTriggerSummarization = async () => {
    try {
      await summarizeMutation.mutateAsync(reportId);
      toast.success('Interpretation updated successfully!');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Interpretation trigger failed.');
    }
  };

  // Copy OCR text
  const handleCopyText = () => {
    if (report?.extracted_text) {
      navigator.clipboard.writeText(report.extracted_text)
        .then(() => {
          toast.success('Extracted text copied');
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        })
        .catch(() => {
          toast.error('Failed to copy text');
        });
    }
  };

  // Copy AI summary
  const handleCopySummary = () => {
    const textToCopy = summaryLanguage === 'en' ? report?.ai_summary : report?.hindi_summary;
    if (textToCopy) {
      navigator.clipboard.writeText(textToCopy)
        .then(() => {
          toast.success(summaryLanguage === 'en' ? 'AI summary copied' : 'नैदानिक सारांश कॉपी किया गया');
          setCopiedSummary(true);
          setTimeout(() => setCopiedSummary(false), 2000);
        })
        .catch(() => toast.error('Failed to copy summary'));
    }
  };

  // Copy patient explanation
  const handleCopyExplanation = () => {
    const textToCopy = language === 'en' ? report?.patient_explanation : report?.hindi_explanation;
    if (textToCopy) {
      navigator.clipboard.writeText(textToCopy)
        .then(() => {
          toast.success(language === 'en' ? 'Patient explanation copied' : 'विवरण कॉपी किया गया');
          setCopiedExplanation(true);
          setTimeout(() => setCopiedExplanation(false), 2000);
        })
        .catch(() => toast.error('Failed to copy explanation'));
    }
  };

  // Download helper
  const downloadText = (filename: string, content: string) => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadAI = () => {
    const textToDownload = summaryLanguage === 'en' ? report?.ai_summary : report?.hindi_summary;
    if (textToDownload && report) {
      const suffix = summaryLanguage === 'en' ? 'AI_Summary' : 'AI_Summary_Hindi';
      const filename = `${report.title?.replace(/\s+/g, '_')}_${suffix}.txt`;
      downloadText(filename, textToDownload);
    } else {
      toast.error('No summary to download');
    }
  };

  const handleDownloadPatient = () => {
    const textToDownload = language === 'en' ? report?.patient_explanation : report?.hindi_explanation;
    if (textToDownload && report) {
      const suffix = language === 'en' ? 'Patient_Explanation' : 'Patient_Explanation_Hindi';
      const filename = `${report.title?.replace(/\s+/g, '_')}_${suffix}.txt`;
      downloadText(filename, textToDownload);
    } else {
      toast.error('No explanation to download');
    }
  };

  const handleDownloadFull = () => {
    const parts = [
      `Title: ${report?.title ?? 'N/A'}`,
      `Status: ${report?.status ?? 'N/A'}`,
      '---',
      'Extracted Text:',
      report?.extracted_text ?? 'N/A',
      '---',
      'AI Summary (English):',
      report?.ai_summary ?? 'N/A',
      '---',
      'AI Summary (Hindi):',
      report?.hindi_summary ?? 'N/A',
      '---',
      'Patient Explanation (English):',
      report?.patient_explanation ?? 'N/A',
      '---',
      'Patient Explanation (Hindi):',
      report?.hindi_explanation ?? 'N/A',
    ];
    const content = parts.join('\n');
    const filename = `${report?.title?.replace(/\s+/g, '_')}_Full_Report.txt`;
    downloadText(filename, content);
  };

  // PDF Exporters
  const exportClinicalPDF = () => {
    const textToExport = summaryLanguage === 'en' ? report?.ai_summary : report?.hindi_summary;
    if (!textToExport || !report) {
      toast.error('No summary to export');
      return;
    }
    const doc = new jsPDF();
    const title = report.title ?? 'Report';
    const date = formatDate(report.created_at);
    const status = report.status ?? '';
    const label = summaryLanguage === 'en' ? 'Clinical Summary' : 'Clinical Summary (Hindi)';
    const content = `${label}:\n${textToExport}`;
    const text = `Title: ${title}\nDate: ${date}\nStatus: ${status}\n\n${content}`;
    const lines = doc.splitTextToSize(text, 180);
    doc.text(lines, 10, 10);
    doc.save(`${title.replace(/\s+/g, '_')}_Clinical_Summary_${summaryLanguage.toUpperCase()}.pdf`);
    toast.success('Clinical PDF exported');
  };

  const exportPatientPDF = () => {
    const textToExport = language === 'en' ? report?.patient_explanation : report?.hindi_explanation;
    if (!textToExport || !report) {
      toast.error('No explanation to export');
      return;
    }
    const doc = new jsPDF();
    const title = report.title ?? 'Report';
    const date = formatDate(report.created_at);
    const status = report.status ?? '';
    const label = language === 'en' ? 'Patient Explanation' : 'Patient Explanation (Hindi)';
    const content = `${label}:\n${textToExport}`;
    const text = `Title: ${title}\nDate: ${date}\nStatus: ${status}\n\n${content}`;
    const lines = doc.splitTextToSize(text, 180);
    doc.text(lines, 10, 10);
    doc.save(`${title.replace(/\s+/g, '_')}_Patient_Explanation_${language.toUpperCase()}.pdf`);
    toast.success('Patient PDF exported');
  };

  const formatBytes = (bytes: number | null): string => {
    if (bytes === null || bytes === undefined) return 'N/A';
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    try {
      return new Date(dateString).toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
      });
    } catch {
      return 'N/A';
    }
  };

  // Bold Text Parser
  const renderBoldText = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index} className="font-extrabold text-slate-900 dark:text-slate-100">{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  // Markdown renderer
  const parseMarkdown = (text: string | null) => {
    if (!text) return <p className="text-slate-600 italic">No summary text available.</p>;

    return text.split('\n').map((line, idx) => {
      const trimmed = line.trim();

      if (trimmed === '') {
        return <div key={idx} className="h-3" />;
      }

      if (trimmed.startsWith('### ')) {
        return (
          <h4 key={idx} className="font-heading font-extrabold text-sm sm:text-base text-slate-800 dark:text-slate-200 mt-6 mb-2 tracking-tight flex items-center gap-1.5 border-b border-slate-100 dark:border-slate-850 pb-1">
            <span>{trimmed.replace('### ', '')}</span>
          </h4>
        );
      }

      if (trimmed.startsWith('## ')) {
        return (
          <h3 key={idx} className="font-heading font-extrabold text-base sm:text-lg text-slate-850 dark:text-slate-100 mt-7 mb-3 tracking-tight border-b border-slate-250/40 dark:border-slate-800/80 pb-1.5">
            {trimmed.replace('## ', '')}
          </h3>
        );
      }

      if (trimmed.startsWith('# ')) {
        return (
          <h2 key={idx} className="font-heading font-extrabold text-lg sm:text-xl text-slate-900 dark:text-slate-50 mt-8 mb-4 tracking-tight">
            {trimmed.replace('# ', '')}
          </h2>
        );
      }

      if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        const content = trimmed.substring(2);
        return (
          <li key={idx} className="list-none relative text-xs sm:text-sm text-slate-800 dark:text-slate-300 mb-2 leading-relaxed pl-5 before:content-['•'] before:absolute before:left-1 before:top-0 before:text-sky-500 before:font-bold">
            {renderBoldText(content)}
          </li>
        );
      }

      return (
        <p key={idx} className="text-xs sm:text-sm text-slate-800 dark:text-slate-350 leading-relaxed mb-3">
          {renderBoldText(trimmed)}
        </p>
      );
    });
  };

  if (isLoading) {
    return <DetailsSkeleton />;
  }

  if (isError || !report) {
    return (
      <div className="max-w-md mx-auto py-12 text-center">
        <Card className="p-8 border-red-200/60 dark:border-red-900/30 bg-red-50/50 dark:bg-red-950/10">
          <h3 className="font-heading text-lg font-bold text-red-700 dark:text-red-400">Record Not Found</h3>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-2">
            {error instanceof Error ? error.message : 'Failed to retrieve report data.'}
          </p>
          <Button variant="outline" className="mt-6" onClick={() => navigate('/')}>
            Back to Dashboard
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Navigation & Actions Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-1.5 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200 text-sm font-semibold transition-colors cursor-pointer w-fit"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>

        <div className="flex items-center gap-2">
          {report.status !== 'pending' && report.status !== 'processing' && (
            <Button
              variant="outline"
              size="sm"
              leftIcon={<RefreshCw className={`w-3.5 h-3.5 ${summarizeMutation.isPending ? 'animate-spin' : ''}`} />}
              onClick={handleTriggerSummarization}
              isLoading={summarizeMutation.isPending}
            >
              Re-Summarize
            </Button>
          )}
        </div>
      </div>

      {/* Main Details Context Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800/80 rounded-3xl p-6 md:p-8 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-6 relative overflow-hidden">
        {/* Glow orb */}
        <div className="absolute right-0 top-0 w-64 h-64 bg-sky-500/5 dark:bg-sky-500/5 rounded-full blur-3xl pointer-events-none -z-10" />

        <div className="space-y-3">
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="text-[10px] font-bold text-slate-600 dark:text-slate-500 tracking-widest uppercase bg-slate-50 dark:bg-slate-950 px-2 py-0.5 border border-slate-200/50 dark:border-slate-800 rounded-md">
              ID: #{report.id}
            </span>
            <Badge status={report.status} />
          </div>

          <h1 className="font-heading font-extrabold text-2xl sm:text-3xl text-slate-800 dark:text-slate-100">
            {report.title}
          </h1>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs font-semibold text-slate-600 dark:text-slate-400">
            <div className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              <span>Created: {formatDate(report.created_at)}</span>
            </div>
            {report.updated_at && (
              <div className="flex items-center gap-1.5 border-l border-slate-200/80 dark:border-slate-800 pl-4">
                <span>Updated: {formatDate(report.updated_at)}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ACTIVE POLLING PROCESSING INTERFACE */}
      {(report.status === 'pending' || report.status === 'processing') && (
        <Card className="p-8 md:p-12 text-center max-w-xl mx-auto space-y-6 bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800/80 shadow-md">
          <div className="relative flex items-center justify-center mx-auto">
            <div className="w-24 h-24 rounded-full border-4 border-slate-100 dark:border-slate-800 border-t-sky-500 animate-spin" />
            <BrainCircuit className="w-10 h-10 text-sky-500 absolute animate-pulse" />
          </div>

          <div className="space-y-2">
            <h3 className="font-heading font-extrabold text-xl text-slate-800 dark:text-slate-250">
              Analyzing Diagnostic Document
            </h3>
            <p className="text-slate-700 dark:text-slate-400 text-sm max-w-sm mx-auto leading-relaxed">
              NeuroScribe is running text extractions, compiling clinical variables, and generating reports using Gemini AI...
            </p>
          </div>

          {/* Stepper tracker */}
          <div className="border-t border-slate-100 dark:border-slate-800/80 pt-6 max-w-sm mx-auto flex justify-between text-xs font-bold text-slate-600">
            <div className="flex flex-col items-center gap-1">
              <span className="w-5 h-5 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-[10px]">✓</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">File Saved</span>
            </div>
            <div className="w-full h-0.5 bg-slate-100 dark:bg-slate-850 self-center mx-2 mb-4" />
            <div className="flex flex-col items-center gap-1">
              <span className={`w-5 h-5 rounded-full flex items-center justify-center font-bold text-[10px] ${report.status === 'processing' ? 'bg-sky-500 text-white animate-pulse' : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
                }`}>{report.status === 'processing' ? '•' : '2'}</span>
              <span className={report.status === 'processing' ? 'text-sky-500 dark:text-sky-400' : ''}>OCR Scan</span>
            </div>
            <div className="w-full h-0.5 bg-slate-100 dark:bg-slate-850 self-center mx-2 mb-4" />
            <div className="flex flex-col items-center gap-1">
              <span className="w-5 h-5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center font-bold text-[10px]">3</span>
              <span>AI Summaries</span>
            </div>
          </div>
        </Card>
      )}

      {/* EXPLAIN FAILED INTERFACE */}
      {report.status === 'failed' && (
        <Card className="p-8 border-rose-200 dark:border-rose-900/30 bg-rose-50/20 dark:bg-rose-950/10 text-center max-w-lg mx-auto space-y-6">
          <div className="w-14 h-14 rounded-2xl bg-rose-50 dark:bg-rose-950/30 border border-rose-100 dark:border-rose-900/30 text-rose-500 dark:text-rose-455 flex items-center justify-center mx-auto shadow-sm">
            <AlertCircle className="w-7 h-7" />
          </div>
          <div className="space-y-2">
            <h3 className="font-heading font-extrabold text-lg text-rose-800 dark:text-rose-350">Processing Pipeline Failed</h3>
            <p className="text-slate-700 dark:text-slate-400 text-sm leading-relaxed">
              We encountered an issue during text extraction or AI interpretation. This can occur with highly stylized, corrupt, or low-resolution documents.
            </p>
          </div>
          <div className="flex gap-3 justify-center">
            <Button
              variant="outline"
              onClick={() => navigate('/')}
            >
              Back to Dashboard
            </Button>
            <Button
              variant="primary"
              leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
              onClick={handleTriggerSummarization}
              isLoading={summarizeMutation.isPending}
            >
              Retry Pipeline
            </Button>
          </div>
        </Card>
      )}

      {/* COMPLETED INTERFACE & WORKSPACE TABS */}
      {report.status === 'completed' && (
        <div className="space-y-6">
          {/* Tabs header row */}
          <div className="flex border-b border-slate-200 dark:border-slate-800">
            <button
              onClick={() => setActiveTab('insights')}
              className={`flex items-center gap-2 px-5 py-3 border-b-2 font-bold text-sm transition-all cursor-pointer relative ${activeTab === 'insights'
                  ? 'border-sky-500 text-sky-600 dark:text-sky-400'
                  : 'border-transparent text-slate-600 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>🧠 AI Medical Evaluation</span>
              {activeTab === 'insights' && <span className="tab-underline" />}
            </button>

            <button
              onClick={() => setActiveTab('text')}
              className={`flex items-center gap-2 px-5 py-3 border-b-2 font-bold text-sm transition-all cursor-pointer relative ${activeTab === 'text'
                  ? 'border-sky-500 text-sky-600 dark:text-sky-400'
                  : 'border-transparent text-slate-600 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
            >
              <FileText className="w-4 h-4" />
              <span>📄 Extracted Document Text</span>
              {activeTab === 'text' && <span className="tab-underline" />}
            </button>

            <button
              onClick={() => setActiveTab('specs')}
              className={`flex items-center gap-2 px-5 py-3 border-b-2 font-bold text-sm transition-all cursor-pointer relative ${activeTab === 'specs'
                  ? 'border-sky-500 text-sky-600 dark:text-sky-400'
                  : 'border-transparent text-slate-600 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
            >
              <HardDrive className="w-4 h-4" />
              <span>📂 File Metadata</span>
              {activeTab === 'specs' && <span className="tab-underline" />}
            </button>
          </div>

          {/* TAB 1: Clinical Insights */}
          {activeTab === 'insights' && (
            isSummaryMissing ? (
              <Card className="p-8 text-center flex flex-col items-center justify-center space-y-4 max-w-lg mx-auto py-12 shadow-sm border border-slate-200/60 dark:border-slate-800/80 bg-white dark:bg-slate-900">
                <div className="w-12 h-12 rounded-xl bg-sky-50 dark:bg-sky-950/40 border border-sky-100/50 dark:border-sky-900/30 text-sky-500 dark:text-sky-400 flex items-center justify-center shadow-sm">
                  <Sparkles className="w-6 h-6 text-sky-500 animate-pulse" />
                </div>
                <div className="space-y-1.5">
                  <h3 className="font-heading font-extrabold text-lg text-slate-800 dark:text-slate-200">Generate AI Interpretation</h3>
                  <p className="text-slate-700 dark:text-slate-450 text-sm max-w-sm leading-relaxed">
                    No clinical summary or patient explanation exists for this report yet. Trigger the AI interpreter to process the extracted text.
                  </p>
                </div>
                <Button
                  variant="primary"
                  leftIcon={<Sparkles className="w-4 h-4" />}
                  onClick={handleTriggerSummarization}
                  isLoading={summarizeMutation.isPending}
                >
                  Generate AI Summary
                </Button>
              </Card>
            ) : (
              <div className="space-y-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Left Column: AI Clinical Summary */}
                  <Card className="flex flex-col h-full bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800/80 shadow-sm border-t-4 border-t-sky-500 rounded-t-xl">
                    <div className="p-5 border-b border-slate-100 dark:border-slate-850 bg-slate-50/50 dark:bg-slate-900/30 flex items-center justify-between gap-3 flex-wrap">
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-lg bg-sky-50 dark:bg-sky-950/40 border border-sky-100/50 dark:border-sky-900/30 text-sky-600 dark:text-sky-400">
                          <BrainCircuit className="w-4.5 h-4.5" />
                        </div>
                        <div>
                          <h3 className="font-heading font-extrabold text-sm text-slate-800 dark:text-slate-200">
                            AI Clinical Summary
                          </h3>
                          <p className="text-[9px] text-slate-600 dark:text-slate-500 font-bold uppercase tracking-widest mt-0.5">
                            Prepared for Clinical Review
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {/* Segmented language control */}
                        <div className="flex bg-slate-100 dark:bg-slate-950 rounded-xl p-0.5 border border-slate-200/50 dark:border-slate-800/60 shadow-inner">
                          <button
                            type="button"
                            onClick={() => setSummaryLanguage('en')}
                            className={`px-3 py-1.5 rounded-lg text-xs font-extrabold transition-all cursor-pointer ${
                              summaryLanguage === 'en'
                                ? 'bg-white dark:bg-slate-800 text-sky-600 dark:text-sky-400 shadow-sm'
                                : 'text-slate-600 hover:text-slate-900 dark:hover:text-slate-300'
                            }`}
                          >
                            English
                          </button>
                          <button
                            type="button"
                            onClick={() => setSummaryLanguage('hi')}
                            className={`px-3 py-1.5 rounded-lg text-xs font-extrabold transition-all cursor-pointer ${
                              summaryLanguage === 'hi'
                                ? 'bg-white dark:bg-slate-800 text-sky-600 dark:text-sky-400 shadow-sm'
                                : 'text-slate-600 hover:text-slate-900 dark:hover:text-slate-300'
                            }`}
                          >
                            हिन्दी
                          </button>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          leftIcon={copiedSummary ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                          onClick={handleCopySummary}
                          disabled={summaryLanguage === 'en' ? !report.ai_summary : !report.hindi_summary}
                        >
                          {copiedSummary ? 'Copied' : 'Copy'}
                        </Button>
                      </div>
                    </div>

                    <div className="p-6 md:p-8 flex-1 prose dark:prose-invert max-w-none text-slate-800 dark:text-slate-300 bg-white dark:bg-slate-900 leading-relaxed max-w-prose">
                      {summaryLanguage === 'en' ? (
                        parseMarkdown(report.ai_summary)
                      ) : (
                        report.hindi_summary ? (
                          parseMarkdown(report.hindi_summary)
                        ) : (
                          <p className="text-slate-600 dark:text-slate-500 italic text-xs font-medium">Hindi summary not generated.</p>
                        )
                      )}
                    </div>
                  </Card>

                  {/* Right Column: Patient Explanation */}
                  <Card className="flex flex-col h-full bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800/80 shadow-sm border-t-4 border-t-indigo-500 rounded-t-xl">
                    <div className="p-5 border-b border-slate-100 dark:border-slate-850 bg-slate-50/50 dark:bg-slate-900/30 flex items-center justify-between gap-3 flex-wrap">
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-100/50 dark:border-indigo-900/30 text-indigo-600 dark:text-indigo-400">
                          <Shield className="w-4.5 h-4.5" />
                        </div>
                        <div>
                          <h3 className="font-heading font-extrabold text-sm text-slate-800 dark:text-slate-200">
                            Patient-Friendly Explanation
                          </h3>
                          <p className="text-[9px] text-slate-600 dark:text-slate-500 font-bold uppercase tracking-widest mt-0.5">
                            Translated for Clear Understanding
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {/* Segmented language control */}
                        <div className="flex bg-slate-100 dark:bg-slate-950 rounded-xl p-0.5 border border-slate-200/50 dark:border-slate-800/60 shadow-inner">
                          <button
                            type="button"
                            onClick={() => setLanguage('en')}
                            className={`px-3 py-1.5 rounded-lg text-xs font-extrabold transition-all cursor-pointer ${
                              language === 'en'
                                ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm'
                                : 'text-slate-600 hover:text-slate-900 dark:hover:text-slate-300'
                            }`}
                          >
                            English
                          </button>
                          <button
                            type="button"
                            onClick={() => setLanguage('hi')}
                            className={`px-3 py-1.5 rounded-lg text-xs font-extrabold transition-all cursor-pointer ${
                              language === 'hi'
                                ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm'
                                : 'text-slate-600 hover:text-slate-900 dark:hover:text-slate-300'
                            }`}
                          >
                            हिन्दी
                          </button>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          leftIcon={copiedExplanation ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                          onClick={handleCopyExplanation}
                          disabled={language === 'en' ? !report.patient_explanation : !report.hindi_explanation}
                        >
                          {copiedExplanation ? 'Copied' : 'Copy'}
                        </Button>
                      </div>
                    </div>

                    <div className="p-6 md:p-8 flex-1 prose dark:prose-invert max-w-none text-slate-800 dark:text-slate-300 bg-white dark:bg-slate-900 flex flex-col justify-between max-w-prose">
                      <div>
                        {language === 'en' ? (
                          parseMarkdown(report.patient_explanation)
                        ) : (
                          report.hindi_explanation ? (
                            parseMarkdown(report.hindi_explanation)
                          ) : (
                            <p className="text-slate-600 dark:text-slate-500 italic text-xs font-medium">Hindi explanation not generated.</p>
                          )
                        )}
                      </div>
                      
                      {language === 'hi' && report.hindi_explanation && (
                        <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-850 text-xs text-amber-800 dark:text-amber-400 font-bold italic bg-amber-500/5 p-4 rounded-xl border border-amber-500/10">
                          ⚠️ यह जानकारी केवल समझाने के उद्देश्य से है। अंतिम चिकित्सा सलाह के लिए डॉक्टर से संपर्क करें।
                        </div>
                      )}
                    </div>
                  </Card>
                </div>

                {/* Combined Action Bar */}
                <div className="flex flex-wrap gap-3 items-center justify-center p-6 bg-slate-50/50 dark:bg-slate-950/20 border border-slate-200/50 dark:border-slate-850 rounded-2xl max-w-4xl mx-auto w-full">
                  <Button variant="outline" leftIcon={<Download className="w-4 h-4" />} onClick={handleDownloadAI} size="sm">
                    AI Summary (.txt)
                  </Button>
                  <Button variant="outline" leftIcon={<Download className="w-4 h-4" />} onClick={handleDownloadPatient} size="sm">
                    Patient Explanation (.txt)
                  </Button>
                  <Button variant="primary" leftIcon={<Download className="w-4 h-4" />} onClick={handleDownloadFull} size="sm">
                    Download Full Report (.txt)
                  </Button>
                  <div className="h-5 w-[1px] bg-slate-200 dark:bg-slate-800 mx-1 hidden sm:block" />
                  <Button variant="outline" leftIcon={<FileCode className="w-4 h-4" />} onClick={exportClinicalPDF} size="sm">
                    Export Clinical PDF
                  </Button>
                  <Button variant="outline" leftIcon={<FileCode className="w-4 h-4" />} onClick={exportPatientPDF} size="sm">
                    Export Patient PDF
                  </Button>
                </div>
              </div>
            )
          )}

          {/* TAB 2: Extracted Text */}
          {activeTab === 'text' && (
            <Card className="border border-slate-200/60 dark:border-slate-800/80 shadow-sm rounded-2xl overflow-hidden bg-white dark:bg-slate-900">
              <div className="p-5 border-b border-slate-100 dark:border-slate-850 bg-slate-50/50 dark:bg-slate-900/30 flex items-center justify-between gap-4">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-100/50 dark:border-emerald-900/30 text-emerald-600 dark:text-emerald-400">
                    <FileCode className="w-4.5 h-4.5" />
                  </div>
                  <div>
                    <h3 className="font-heading font-extrabold text-sm text-slate-800 dark:text-slate-200">
                      OCR Extracted Document Text
                    </h3>
                    <p className="text-[9px] text-slate-600 dark:text-slate-500 font-bold uppercase tracking-widest mt-0.5">
                      Raw plaintext read by OCR pipeline
                    </p>
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  onClick={handleCopyText}
                  disabled={!report.extracted_text}
                >
                  {copied ? 'Copied' : 'Copy Text'}
                </Button>
              </div>

              <div className="p-6 bg-slate-950 overflow-x-auto border-t border-slate-900 shadow-inner">
                {report.extracted_text ? (
                  <pre className="text-slate-300 dark:text-slate-400 font-mono text-xs sm:text-sm leading-relaxed whitespace-pre-wrap max-h-[500px]">
                    {report.extracted_text}
                  </pre>
                ) : (
                  <p className="text-slate-400 dark:text-slate-500 italic text-xs font-mono text-center py-6">
                    No OCR plain text was extracted from this report file.
                  </p>
                )}
              </div>
            </Card>
          )}

          {/* TAB 3: File Specifications */}
          {activeTab === 'specs' && (
            <Card className="border border-slate-200/60 dark:border-slate-800/80 shadow-sm rounded-2xl max-w-3xl mx-auto bg-white dark:bg-slate-900">
              <div className="p-5 border-b border-slate-100 dark:border-slate-850 bg-slate-50/50 dark:bg-slate-900/30 flex items-center gap-2.5">
                <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-300">
                  <HardDrive className="w-4.5 h-4.5" />
                </div>
                <div>
                  <h3 className="font-heading font-extrabold text-sm text-slate-800 dark:text-slate-200">
                    Document System Properties
                  </h3>
                  <p className="text-[9px] text-slate-600 dark:text-slate-500 font-bold uppercase tracking-widest mt-0.5">
                    Physical attributes and server storage metrics
                  </p>
                </div>
              </div>

              <div className="p-6 divide-y divide-slate-100 dark:divide-slate-850 text-xs sm:text-sm">
                <div className="py-3 flex items-center justify-between gap-4">
                  <span className="font-bold text-slate-700 dark:text-slate-550 uppercase tracking-widest text-[9px] self-center">Original Filename</span>
                  <span className="font-mono text-slate-800 dark:text-slate-200 break-all select-all font-semibold">{report.original_filename || 'N/A'}</span>
                </div>
                <div className="py-3 flex items-center justify-between gap-4">
                  <span className="font-bold text-slate-700 dark:text-slate-550 uppercase tracking-widest text-[9px] self-center">Database Status</span>
                  <Badge status={report.status} className="scale-90" />
                </div>
                <div className="py-3 flex items-center justify-between gap-4">
                  <span className="font-bold text-slate-700 dark:text-slate-550 uppercase tracking-widest text-[9px] self-center">File Mime / Type</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-300 uppercase font-mono">{report.file_type || 'N/A'}</span>
                </div>
                <div className="py-3 flex items-center justify-between gap-4">
                  <span className="font-bold text-slate-700 dark:text-slate-550 uppercase tracking-widest text-[9px]">File Size</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{formatBytes(report.file_size_bytes)} ({report.file_size_bytes?.toLocaleString() || 0} bytes)</span>
                </div>
                <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <span className="font-bold text-slate-700 dark:text-slate-550 uppercase tracking-widest text-[9px] self-start sm:self-center">Disk Storage Path</span>
                  <span className="font-mono text-slate-600 dark:text-slate-400 break-all text-xs bg-slate-50 dark:bg-slate-950 border border-slate-200/50 dark:border-slate-800/80 px-2.5 py-1 rounded-md">{report.file_path || 'N/A'}</span>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
