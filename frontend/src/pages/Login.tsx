import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Placeholder authentication logic
    console.log('Logging in with', { email, password });
    // After successful login, navigate to dashboard
    navigate('/');
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-50 dark:bg-slate-900">
      <Card className="w-full max-w-md p-8 space-y-6">
        <h2 className="text-2xl font-bold text-center text-slate-900 dark:text-white">Login</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            id="email"
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            id="password"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button type="submit" variant="primary" className="w-full">
            Sign In
          </Button>
        </form>
        <div className="text-center">
          <span className="text-sm text-slate-700 dark:text-slate-400">
            Don’t have an account?{' '}
            <a
              href="/signup"
              className="font-medium text-sky-600 hover:underline"
            >
              Sign Up
            </a>
          </span>
        </div>
      </Card>
    </div>
  );
};
