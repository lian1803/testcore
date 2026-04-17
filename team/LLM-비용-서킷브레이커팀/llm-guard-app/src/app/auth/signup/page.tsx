'use client';

import { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { Check } from 'lucide-react';

function SignupContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [oauthError, setOauthError] = useState<string | null>(null);

  useEffect(() => {
    const error = searchParams.get('error');
    if (error === 'oauth_denied') {
      setOauthError('Google sign-up was cancelled.');
    } else if (error === 'oauth_failed') {
      setOauthError('Google sign-up failed. Please try again.');
    }
  }, [searchParams]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        toast.error(data.error?.message || 'Signup failed. Please try again.');
        return;
      }

      toast.success('Account created successfully');
      router.push('/dashboard');
    } catch (error) {
      console.error('[Signup Error]', error);
      toast.error('Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    'Real-time cost tracking',
    'Agent loop detection',
    'Multi-project budgets',
    'Slack & Email alerts',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0d1117] to-[#161b22] flex items-center justify-center px-4">
      <div className="w-full max-w-4xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          {/* Left: Features */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="hidden md:block">
              <h2 className="text-3xl font-bold mb-6">Get Started Today</h2>
              <div className="space-y-4">
                {features.map((feature, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-[#00ff88]/20 flex items-center justify-center flex-shrink-0">
                      <Check size={14} className="text-[#00ff88]" />
                    </div>
                    <span className="text-[#8b949e]">{feature}</span>
                  </div>
                ))}
              </div>

              <div className="mt-8 p-4 bg-[#161b22] border border-[#30363d] rounded-lg">
                <p className="text-sm text-[#6e7681] mb-2">Trusted by teams at:</p>
                <p className="text-[#8b949e]">Anthropic, OpenAI, DeepSeek...</p>
              </div>
            </div>
          </motion.div>

          {/* Right: Form */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Card className="bg-[#161b22] border-[#30363d]">
              <CardHeader className="text-center">
                <div className="text-4xl font-bold text-[#00ff88] mb-4">LLM Guard</div>
                <CardTitle>Create Your Account</CardTitle>
                <p className="text-sm text-[#8b949e] mt-2">
                  Protect your LLM API spend in minutes
                </p>
              </CardHeader>

              <CardContent>
                {oauthError && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm"
                  >
                    {oauthError}
                  </motion.div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="name" className="text-[#8b949e]">
                      Full Name
                    </Label>
                    <Input
                      id="name"
                      name="name"
                      placeholder="Jane Doe"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      className="mt-2 bg-[#0d1117] border-[#30363d]"
                    />
                  </div>

                  <div>
                    <Label htmlFor="email" className="text-[#8b949e]">
                      Email
                    </Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="you@company.com"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="mt-2 bg-[#0d1117] border-[#30363d]"
                    />
                  </div>

                  <div>
                    <Label htmlFor="password" className="text-[#8b949e]">
                      Password
                    </Label>
                    <Input
                      id="password"
                      name="password"
                      type="password"
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      className="mt-2 bg-[#0d1117] border-[#30363d]"
                    />
                  </div>

                  <div>
                    <Label htmlFor="confirmPassword" className="text-[#8b949e]">
                      Confirm Password
                    </Label>
                    <Input
                      id="confirmPassword"
                      name="confirmPassword"
                      type="password"
                      placeholder="••••••••"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      required
                      className="mt-2 bg-[#0d1117] border-[#30363d]"
                    />
                  </div>

                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-[#00ff88] text-[#0d1117] font-bold"
                  >
                    {isLoading ? 'Creating account...' : 'Create Account'}
                  </Button>
                </form>

                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-[#30363d]" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-[#161b22] text-[#6e7681]">Or sign up with</span>
                  </div>
                </div>

                <a href="/api/auth/google" className="block">
                  <Button
                    type="button"
                    variant="outline"
                    className="w-full border-[#30363d] text-[#8b949e] hover:bg-[#21262d] flex items-center justify-center gap-2"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      width="18"
                      height="18"
                      className="fill-current"
                    >
                      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                    </svg>
                    Google로 회원가입
                  </Button>
                </a>

                <p className="text-center text-sm text-[#6e7681] mt-6">
                  Already have an account?{' '}
                  <Link href="/auth/login" className="text-[#00ff88] hover:underline">
                    Sign in
                  </Link>
                </p>

                <p className="text-center text-xs text-[#6e7681] mt-4">
                  By creating an account, you agree to our{' '}
                  <a href="#" className="underline hover:text-[#8b949e]">
                    Terms of Service
                  </a>{' '}
                  and{' '}
                  <a href="#" className="underline hover:text-[#8b949e]">
                    Privacy Policy
                  </a>
                </p>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

export default function SignupPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#0d1117] flex items-center justify-center"><div className="w-8 h-8 border-2 border-[#00ff88]/30 border-t-[#00ff88] rounded-full animate-spin" /></div>}>
      <SignupContent />
    </Suspense>
  );
}
