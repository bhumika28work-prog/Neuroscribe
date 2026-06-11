// src/design/Hero.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { ArrowRight, Sparkles } from 'lucide-react';

export interface HeroProps {
  title?: string;
  subtitle?: string;
  ctaText?: string;
  onCtaClick?: () => void;
  leftIcon?: React.ReactNode;
}

export const Hero: React.FC<HeroProps> = ({
  title = 'NeuroScribe AI',
  subtitle = 'AI Powered Medical Report Analysis',
  ctaText = 'Upload Report',
  onCtaClick,
  leftIcon,
}) => {
  const navigate = useNavigate();
  const handleClick = () => {
    if (onCtaClick) {
      onCtaClick();
    } else {
      navigate('/upload');
    }
  };

  return (
    <section className="relative overflow-hidden rounded-3xl bg-slate-900 text-white shadow-2xl border border-slate-800 transition-all duration-500 py-12 px-6 md:py-16 md:px-12 lg:py-20 lg:px-16">
      {/* Dynamic background mesh gradient */}
      <div className="absolute inset-0 bg-gradient-to-tr from-indigo-950 via-slate-900 to-sky-950/80 opacity-90 z-0" />
      
      {/* Decorative floating blurred gradient mesh */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-sky-500/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-32 -left-32 w-[450px] h-[450px] bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />
      
      {/* Grid overlay */}
      <div 
        className="absolute inset-0 opacity-[0.02] pointer-events-none z-0" 
        style={{
          backgroundImage: `radial-gradient(circle, white 1px, transparent 1px)`,
          backgroundSize: '24px 24px'
        }}
      />

      <div className="relative z-10 flex flex-col items-center text-center max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-sky-500/10 text-sky-400 border border-sky-500/20 shadow-inner">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Next-Generation Healthcare Intelligence</span>
        </div>

        <h1 className="font-heading text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-[1.1] text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-slate-300">
          {title}
        </h1>
        
        <p className="max-w-2xl text-slate-300 text-sm sm:text-base md:text-lg leading-relaxed">
          {subtitle}
        </p>

        <div className="pt-4">
          <Button
            variant="primary"
            size="lg"
            leftIcon={leftIcon ?? <ArrowRight className="w-5 h-5" />}
            onClick={handleClick}
            className="shadow-xl shadow-sky-500/20 active:scale-95 transition-transform"
          >
            {ctaText}
          </Button>
        </div>
      </div>
    </section>
  );
};
