import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, AlertTriangle } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex-1 flex flex-col items-center justify-center py-12 text-center">
      <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-rose-50 text-rose-500 border border-rose-100/50 mb-6 shadow-sm">
        <AlertTriangle className="w-8 h-8" />
      </div>

      <h1 className="font-heading font-extrabold text-4xl text-slate-900 tracking-tight mb-3">
        404 - Page Not Found
      </h1>
      
      <p className="max-w-md text-slate-500 text-base leading-relaxed mb-8">
        We searched our records thoroughly but could not find the medical report analyzer page or resources you were requesting.
      </p>

      <Button
        variant="primary"
        leftIcon={<Home className="w-4 h-4" />}
        onClick={() => navigate('/')}
      >
        Back to Dashboard
      </Button>
    </div>
  );
};
