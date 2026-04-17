'use client';

import { Suspense, useState } from 'react';
import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { CodeCompare } from '@/components/landing/code-compare';
import Link from 'next/link';

const HeroScene = dynamic(() => import('@/components/landing/hero-scene').then(m => ({ default: m.HeroScene })), {
  ssr: false,
  loading: () => (
    <div className="w-full h-screen bg-gradient-to-b from-[#0d1117] to-[#161b22] flex items-center justify-center">
      <div className="text-center">
        <div className="w-12 h-12 border-2 border-[#00ff88]/30 border-t-[#00ff88] rounded-full animate-spin mx-auto mb-4" />
        <p className="text-[#8b949e]">Initializing scene...</p>
      </div>
    </div>
  ),
});

export default function Home() {
  const [email, setEmail] = useState('');
  const [waitlistCount] = useState(47);

  const handleWaitlist = (e: React.FormEvent) => {
    e.preventDefault();
    alert('Thanks for joining!');
    setEmail('');
  };

  return (
    <main className="w-full bg-[#0d1117] text-[#e6edf3]">
      {/* HERO SECTION */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <Suspense
            fallback={
              <div className="w-full h-full bg-gradient-to-b from-[#0d1117] to-[#161b22]" />
            }
          >
            <HeroScene />
          </Suspense>
        </div>

        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center pointer-events-none">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="text-center max-w-3xl px-4 pointer-events-auto"
          >
            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="text-5xl md:text-7xl font-bold mb-4 tracking-tight"
              style={{
                textShadow: '0 0 40px rgba(255, 68, 68, 0.3)',
              }}
            >
              <span className="text-[#ff4444]">$72,000</span>
            </motion.h1>

            <motion.h2
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="text-4xl md:text-5xl font-bold mb-8"
              style={{
                color: '#00ff88',
                textShadow: '0 0 40px rgba(0, 255, 136, 0.3)',
              }}
            >
              하룻밤에 날아갔다
            </motion.h2>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 1.0 }}
              className="text-2xl font-bold mb-8 text-[#00ff88]"
              style={{
                textShadow: '0 0 20px rgba(0, 255, 136, 0.2)',
              }}
            >
              한 줄로 막는다
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 1.2 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Button
                size="lg"
                className="bg-[#00ff88] text-[#0d1117] font-bold hover:bg-[#00ff88]/90 pointer-events-auto"
              >
                Join Waitlist
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-[#00ff88]/50 text-[#00ff88] hover:bg-[#00ff88]/10 pointer-events-auto"
              >
                How It Works
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* PROBLEM SECTION */}
      <section className="py-20 px-4 bg-[#0d1117] border-t border-[#30363d]">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">Real Costs. Real Problem.</h2>
            <p className="text-[#8b949e] max-w-2xl mx-auto">
              Teams lost real money. Agent loops, fine-tuning runaway, one mistake costs thousands.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { amount: '82K', cause: 'Agent loop (6h)', team: 'Fintech' },
              { amount: '72K', cause: 'Fine-tuning', team: 'ML Platform' },
              { amount: '47K', cause: 'Unoptimized RAG', team: 'Search' },
            ].map((incident, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: idx * 0.1 }}
                className="bg-[#161b22] border border-[#30363d] rounded-lg p-6"
              >
                <div className="text-3xl font-mono font-bold text-[#ff4444] mb-2">
                  ${incident.amount}
                </div>
                <div className="text-sm text-[#8b949e] mb-4">{incident.cause}</div>
                <div className="text-xs text-[#6e7681]">{incident.team}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* SOLUTION SECTION */}
      <section className="py-20 px-4 bg-[#0d1117] border-t border-[#30363d]">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">One Line. Full Protection.</h2>
            <p className="text-[#8b949e] max-w-2xl mx-auto">
              Drop in. No proxy. Zero latency.
            </p>
          </motion.div>

          <CodeCompare />
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="py-20 px-4 bg-[#0d1117] border-t border-[#30363d]">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">How It Works</h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                num: '1',
                title: 'Install',
                desc: 'Replace OpenAI import with LLM Guard in one line.',
              },
              {
                num: '2',
                title: 'Detect',
                desc: 'Real-time pattern matching identifies loops and anomalies.',
              },
              {
                num: '3',
                title: 'Block',
                desc: 'Interrupt calls. Send alerts. Stay in control.',
              },
            ].map((step, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: idx * 0.1 }}
                className="relative"
              >
                <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-8">
                  <div className="text-5xl font-bold text-[#00ff88] mb-4">{step.num}</div>
                  <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                  <p className="text-[#8b949e]">{step.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* WAITLIST */}
      <section className="py-20 px-4 bg-[#161b22] border-t border-[#30363d]">
        <div className="max-w-2xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl font-bold mb-4">Join the Waitlist</h2>
            <p className="text-[#8b949e] mb-8">
              Early access starts next week.
            </p>

            <form onSubmit={handleWaitlist} className="flex flex-col sm:flex-row gap-2">
              <Input
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="bg-[#0d1117] border-[#30363d]"
              />
              <Button
                type="submit"
                className="bg-[#00ff88] text-[#0d1117] font-bold"
              >
                Join Now
              </Button>
            </form>

            <p className="text-sm text-[#6e7681] mt-4">
              {waitlistCount}+ developers waiting
            </p>
          </motion.div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-[#0d1117] border-t border-[#30363d] py-8 px-4">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center text-[#6e7681] text-sm">
          <div>© 2024 LLM Guard.</div>
          <div className="flex gap-6 mt-4 md:mt-0">
            <Link href="/pricing" className="hover:text-[#00ff88]">
              Pricing
            </Link>
            <Link href="/docs" className="hover:text-[#00ff88]">
              Docs
            </Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
