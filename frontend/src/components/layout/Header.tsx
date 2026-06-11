import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { Brain, Upload, Activity, Sun, Moon } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

export const Header: React.FC = () => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 w-full bg-white/70 dark:bg-slate-950/70 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800/60 shadow-sm transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo / Brand */}
          <Link to="/" className="flex items-center gap-2.5 transition-transform duration-200 active:scale-[0.98]">
            <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 via-blue-600 to-indigo-600 text-white shadow-md shadow-sky-500/10">
              <Brain className="w-5 h-5 animate-pulse" />
            </div>
            <span className="font-heading font-extrabold text-xl tracking-tight bg-gradient-to-r from-slate-900 to-indigo-950 dark:from-white dark:to-slate-200 bg-clip-text text-transparent">
              NeuroScribe
            </span>
          </Link>

          {/* Navigation Items */}
          <nav className="hidden md:flex items-center gap-1.5">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-300 border ${
                  isActive
                    ? 'bg-sky-50 border-sky-100/50 text-sky-600 font-bold dark:bg-sky-500/10 dark:border-sky-500/20 dark:text-sky-400'
                    : 'text-slate-700 dark:text-slate-300 hover:text-slate-950 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800 border-transparent'
                }`
              }
            >
              <Activity className="w-4 h-4" />
              <span>Dashboard</span>
            </NavLink>

            <NavLink
              to="/upload"
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-300 border ${
                  isActive
                    ? 'bg-sky-50 border-sky-100/50 text-sky-600 font-bold dark:bg-sky-500/10 dark:border-sky-500/20 dark:text-sky-400'
                    : 'text-slate-700 dark:text-slate-300 hover:text-slate-950 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800 border-transparent'
                }`
              }
            >
              <Upload className="w-4 h-4" />
              <span>Upload Report</span>
            </NavLink>
          </nav>

          {/* Theme & Auth Buttons */}
          <div className="flex items-center gap-3">
            {/* Theme toggle button */}
            <button
              onClick={toggleTheme}
              className="p-2.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-400 transition-colors cursor-pointer"
              aria-label="Toggle dark mode"
            >
              {isDark ? <Sun className="w-4.5 h-4.5 text-yellow-400" /> : <Moon className="w-4.5 h-4.5 text-slate-600" />}
            </button>
            
            {/* Split/Vertical Line */}
            <div className="h-5 w-[1px] bg-slate-200 dark:bg-slate-800" />

            {/* Auth Actions */}
            <nav className="flex items-center gap-1.5">
              <Link 
                to="/login" 
                className="px-3.5 py-2 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
              >
                Login
              </Link>
              <Link 
                to="/signup" 
                className="px-4 py-2 text-sm font-bold bg-gradient-to-tr from-sky-500 via-blue-600 to-indigo-600 text-white rounded-xl hover:shadow-lg hover:shadow-sky-500/10 active:scale-[0.97] transition-all"
              >
                Sign Up
              </Link>
            </nav>
          </div>
        </div>
      </div>
    </header>
  );
};
