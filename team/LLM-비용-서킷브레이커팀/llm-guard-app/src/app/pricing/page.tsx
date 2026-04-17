'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import Link from 'next/link';
import { Check } from 'lucide-react';

const plans = [
  {
    name: 'Free',
    monthlyPrice: 0,
    annualPrice: 0,
    description: 'Perfect for getting started',
    cta: 'Start Now',
    features: [
      'Basic cost tracking',
      '1 project',
      'Email alerts',
      'Manual budget setting',
      'Community support',
      'Up to 100K requests/month',
    ],
  },
  {
    name: 'Pro',
    monthlyPrice: 49,
    annualPrice: 39,
    description: 'For growing teams',
    cta: 'Start 14-Day Free Trial',
    featured: true,
    features: [
      'Real-time cost tracking',
      'Unlimited projects',
      'Slack + Email alerts',
      'Agent loop detection',
      'Priority support',
      'Up to 10M requests/month',
      'Budget caps per project',
      'Custom thresholds',
      'Team collaboration',
    ],
  },
  {
    name: 'Team',
    monthlyPrice: 199,
    annualPrice: 159,
    description: 'For enterprises',
    cta: 'Contact Sales',
    features: [
      'Everything in Pro',
      'SSO / SAML',
      'Custom integrations',
      'Dedicated account manager',
      'SLA guarantee',
      'Unlimited requests',
      'Audit logs',
      'Advanced reporting',
      'Custom contracts',
    ],
  },
];

const faqs = [
  {
    q: 'Can I cancel anytime?',
    a: 'Yes! All plans are month-to-month with no long-term commitment. You can cancel anytime before the next billing cycle.',
  },
  {
    q: 'How do you calculate usage?',
    a: 'We count actual API calls to LLM providers. Our SDK intercepts requests at the import level, so there\'s no sampling or estimation.',
  },
  {
    q: 'What happens if I exceed my request limit?',
    a: 'We\'ll notify you before you hit the limit. You can upgrade anytime or set a lower budget cap to prevent overspend.',
  },
  {
    q: 'Do you store my API keys?',
    a: 'Never. LLM Guard is a zero-proxy solution. Your API keys stay in your code and never leave your servers. We only track tokens and costs.',
  },
];

export default function PricingPage() {
  const [isAnnual, setIsAnnual] = useState(false);

  return (
    <main className="min-h-screen bg-[#0d1117] text-[#e6edf3]">
      {/* Header */}
      <header className="bg-[#161b22] border-b border-[#30363d] py-4 px-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Link href="/" className="text-xl font-bold">
            LLM Guard
          </Link>
          <nav className="flex gap-6">
            <Link href="/" className="text-sm hover:text-[#00ff88]">
              Home
            </Link>
            <Link href="/dashboard" className="text-sm hover:text-[#00ff88]">
              Dashboard
            </Link>
          </nav>
        </div>
      </header>

      {/* Pricing Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          {/* Hero */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h1 className="text-5xl font-bold mb-4">Simple, transparent pricing</h1>
            <p className="text-lg text-[#8b949e] mb-8">
              Pay only for what you use. No hidden fees.
            </p>

            {/* Toggle */}
            <div className="flex items-center justify-center gap-4 bg-[#161b22] rounded-lg w-fit mx-auto p-1">
              <button
                onClick={() => setIsAnnual(false)}
                className={`px-6 py-2 rounded-md font-medium transition-colors ${
                  !isAnnual
                    ? 'bg-[#00ff88] text-[#0d1117]'
                    : 'text-[#8b949e] hover:text-[#e6edf3]'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setIsAnnual(true)}
                className={`px-6 py-2 rounded-md font-medium transition-colors flex items-center gap-2 ${
                  isAnnual
                    ? 'bg-[#00ff88] text-[#0d1117]'
                    : 'text-[#8b949e] hover:text-[#e6edf3]'
                }`}
              >
                Annual
                <Badge className="bg-[#f0c040]/20 text-[#f0c040] text-xs">
                  20% off
                </Badge>
              </button>
            </div>
          </motion.div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            {plans.map((plan, idx) => {
              const displayPrice = isAnnual ? plan.annualPrice : plan.monthlyPrice;
              const regularPrice = isAnnual
                ? plan.monthlyPrice * 12
                : plan.monthlyPrice;

              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: idx * 0.1 }}
                  className={`relative rounded-lg transition-all ${
                    plan.featured
                      ? 'border border-[#00ff88]/50 bg-gradient-to-b from-[#0d1117] to-[#161b22] ring-2 ring-[#00ff88]/20 transform md:scale-105'
                      : 'border border-[#30363d] bg-[#161b22]'
                  }`}
                >
                  {plan.featured && (
                    <div className="absolute -top-3 left-4">
                      <Badge className="bg-[#00ff88] text-[#0d1117] font-bold">
                        Most Popular
                      </Badge>
                    </div>
                  )}

                  <div className="p-8">
                    <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                    <p className="text-sm text-[#8b949e] mb-6">{plan.description}</p>

                    {/* Price */}
                    <div className="mb-6">
                      {plan.monthlyPrice === 0 ? (
                        <div className="text-4xl font-bold">Free</div>
                      ) : (
                        <div>
                          <div className="text-5xl font-bold font-mono">
                            ${displayPrice}
                          </div>
                          {isAnnual && plan.monthlyPrice > 0 && (
                            <p className="text-sm text-[#6e7681] mt-1">
                              ${plan.monthlyPrice}/month (billed annually)
                            </p>
                          )}
                          {!isAnnual && plan.monthlyPrice > 0 && (
                            <p className="text-sm text-[#6e7681] mt-1">
                              /month, billed monthly
                            </p>
                          )}
                        </div>
                      )}
                    </div>

                    {/* CTA */}
                    <Button
                      className={`w-full mb-8 font-bold ${
                        plan.featured
                          ? 'bg-[#00ff88] text-[#0d1117] hover:bg-[#00ff88]/90'
                          : 'border border-[#00ff88] text-[#00ff88] hover:bg-[#00ff88]/10'
                      }`}
                    >
                      {plan.cta}
                    </Button>

                    {/* Features */}
                    <div className="space-y-3">
                      {plan.features.map((feature, fIdx) => (
                        <div key={fIdx} className="flex items-start gap-3">
                          <Check className="text-[#00ff88] flex-shrink-0 w-5 h-5 mt-0.5" />
                          <span className="text-sm">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Trust Signals */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="bg-[#161b22] border border-[#30363d] rounded-lg p-8 mb-16"
          >
            <h3 className="text-xl font-bold mb-6 text-center">Why choose LLM Guard?</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-3xl mb-2">🔒</div>
                <p className="font-bold mb-2">No Proxy</p>
                <p className="text-sm text-[#8b949e]">
                  Zero-proxy architecture. Your API keys never leave your servers.
                </p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-2">⚡</div>
                <p className="font-bold mb-2">Zero Latency</p>
                <p className="text-sm text-[#8b949e]">
                  Local cost calculation. No network overhead. Production-ready.
                </p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-2">📜</div>
                <p className="font-bold mb-2">MIT License</p>
                <p className="text-sm text-[#8b949e]">
                  Open-source SDK. Full transparency. Use anywhere.
                </p>
              </div>
            </div>
          </motion.div>

          {/* FAQ */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="max-w-2xl mx-auto"
          >
            <h2 className="text-3xl font-bold text-center mb-8">FAQ</h2>
            <div className="space-y-3">
              {faqs.map((faq, idx) => (
                <div
                  key={idx}
                  className="bg-[#161b22] border border-[#30363d] rounded-lg px-6"
                >
                  <div className="text-left font-medium py-4 text-[#e6edf3] hover:text-[#00ff88] cursor-pointer">
                    {faq.q}
                  </div>
                  <div className="text-[#8b949e] pb-4">{faq.a}</div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-[#161b22] border-t border-[#30363d] py-16 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to protect your spend?</h2>
          <p className="text-[#8b949e] mb-8">
            Get started with LLM Guard today. No credit card required.
          </p>
          <Button className="bg-[#00ff88] text-[#0d1117] font-bold text-lg px-8 py-6">
            Start Free Trial
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#0d1117] border-t border-[#30363d] py-8 px-4">
        <div className="max-w-6xl mx-auto text-center text-[#6e7681] text-sm">
          <p>© 2024 LLM Guard. All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}
