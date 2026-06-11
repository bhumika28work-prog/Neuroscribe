import React from 'react';
import { Header } from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="relative min-h-screen flex flex-col bg-slate-50/20 dark:bg-slate-950/30 transition-colors duration-300">
      {/* Premium subtle background glow meshes */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-sky-400/10 dark:bg-sky-500/5 rounded-full blur-3xl pointer-events-none -z-10 animate-pulse duration-10000" />
      <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-indigo-300/10 dark:bg-indigo-500/5 rounded-full blur-3xl pointer-events-none -z-10 animate-pulse duration-8000" />

      {/* Sticky Glass Navigation */}
      <Header />

      {/* Primary Page Canvas */}
      <main className="flex-1 flex flex-col max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        {children}
      </main>

      {/* Sub footer */}
      <footer className="py-6 text-center text-xs text-slate-500 dark:text-slate-500 border-t border-slate-200/50 dark:border-slate-800 bg-white/30 dark:bg-slate-950/40 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4">
          &copy; {new Date().getFullYear()} NeuroScribe. Designed for clinical and medical analysis excellence.
        </div>
      </footer>
    </div>
  );
};
