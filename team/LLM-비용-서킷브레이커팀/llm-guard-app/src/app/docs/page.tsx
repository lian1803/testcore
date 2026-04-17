'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { Copy, Check } from 'lucide-react';

export default function DocsPage() {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const copyToClipboard = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const tabs = [
    { label: 'JavaScript', value: 'js', icon: '⚡' },
    { label: 'Python', value: 'py', icon: '🐍' },
  ];

  const codeExamples = {
    js: {
      install: 'npm install llm-guard-sdk',
      init: `import { LLMGuard } from 'llm-guard-sdk';

const guard = new LLMGuard({
  apiKey: 'lg_your_api_key',
  projectId: 'your_project_id'
});`,
      usage: `// Check before calling LLM API
const check = await guard.check({
  model: 'gpt-4',
  provider: 'openai',
  estimatedTokens: 1000
});

if (check.allowed) {
  const response = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: 'Hello' }]
  });

  // Report actual usage
  await guard.report({
    model: 'gpt-4',
    provider: 'openai',
    inputTokens: response.usage.prompt_tokens,
    outputTokens: response.usage.completion_tokens,
    costUsd: check.estimatedCostUsd,
    isBlocked: false
  });
} else {
  console.log('Budget exceeded:', check.remainingUsd);
}`,
    },
    py: {
      install: 'pip install llm-guard',
      init: `from llm_guard import LLMGuard

guard = LLMGuard(
    api_key='lg_your_api_key',
    project_id='your_project_id'
)`,
      usage: `# Check before calling LLM API
check = guard.check(
    model='gpt-4',
    provider='openai',
    estimated_tokens=1000
)

if check['allowed']:
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[{'role': 'user', 'content': 'Hello'}]
    )

    # Report actual usage
    guard.report(
        model='gpt-4',
        provider='openai',
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        cost_usd=check['estimated_cost_usd'],
        is_blocked=False
    )
else:
    print(f"Budget exceeded. Remaining: \${check['remaining_usd']}")`,
    },
  };

  const [activeLanguage, setActiveLanguage] = useState<'js' | 'py'>('js');

  const CodeBlock = ({
    code,
    language,
    id,
  }: {
    code: string;
    language: string;
    id: string;
  }) => (
    <div className="relative bg-[#0d1117] border border-[#30363d] rounded-lg overflow-hidden">
      <button
        onClick={() => copyToClipboard(code, id)}
        className="absolute top-3 right-3 p-2 bg-[#161b22] hover:bg-[#21262d] rounded transition-colors"
        title="Copy code"
      >
        {copiedCode === id ? (
          <Check size={16} className="text-[#00ff88]" />
        ) : (
          <Copy size={16} className="text-[#8b949e]" />
        )}
      </button>
      <pre className="p-4 overflow-x-auto">
        <code className="text-sm text-[#8b949e] font-mono">{code}</code>
      </pre>
    </div>
  );

  return (
    <main className="min-h-screen bg-[#0d1117] text-[#e6edf3]">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-[#0d1117] border-b border-[#30363d]">
        <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-[#00ff88]">
            LLM Guard
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/pricing" className="text-[#8b949e] hover:text-[#00ff88]">
              Pricing
            </Link>
            <Link href="/auth/login">
              <Button
                variant="outline"
                size="sm"
                className="border-[#30363d] text-[#8b949e]"
              >
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-16">
        {/* Hero */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-20 text-center"
        >
          <h1 className="text-5xl font-bold mb-4">SDK Documentation</h1>
          <p className="text-[#8b949e] text-xl mb-8">
            Integrate LLM Guard into your application with just a few lines of code.
          </p>
          <Link href="/auth/signup">
            <Button className="bg-[#00ff88] text-[#0d1117] font-bold">
              Get Started Free
            </Button>
          </Link>
        </motion.section>

        {/* Quick Start */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-20"
        >
          <h2 className="text-3xl font-bold mb-8">Quick Start</h2>

          <div className="space-y-8">
            {/* Step 1 */}
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-8">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 rounded-full bg-[#00ff88] text-[#0d1117] flex items-center justify-center font-bold">
                  1
                </div>
                <h3 className="text-xl font-bold">Install SDK</h3>
              </div>
              <CodeBlock
                code={codeExamples[activeLanguage].install}
                language={activeLanguage}
                id="install"
              />
            </div>

            {/* Step 2 */}
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-8">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 rounded-full bg-[#00ff88] text-[#0d1117] flex items-center justify-center font-bold">
                  2
                </div>
                <h3 className="text-xl font-bold">Initialize</h3>
              </div>
              <p className="text-[#8b949e] mb-4">
                Get your API key from the{' '}
                <Link href="/auth/login" className="text-[#00ff88] hover:underline">
                  dashboard
                </Link>
              </p>
              <CodeBlock
                code={codeExamples[activeLanguage].init}
                language={activeLanguage}
                id="init"
              />
            </div>

            {/* Step 3 */}
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-8">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 rounded-full bg-[#00ff88] text-[#0d1117] flex items-center justify-center font-bold">
                  3
                </div>
                <h3 className="text-xl font-bold">Wrap Your LLM Calls</h3>
              </div>

              {/* Language Tabs */}
              <div className="flex gap-2 mb-4 border-b border-[#30363d]">
                {tabs.map((tab) => (
                  <button
                    key={tab.value}
                    onClick={() => setActiveLanguage(tab.value as 'js' | 'py')}
                    className={`px-4 py-2 font-medium transition-colors ${
                      activeLanguage === tab.value
                        ? 'text-[#00ff88] border-b-2 border-[#00ff88]'
                        : 'text-[#8b949e] hover:text-[#e6edf3]'
                    }`}
                  >
                    {tab.icon} {tab.label}
                  </button>
                ))}
              </div>

              <CodeBlock
                code={codeExamples[activeLanguage].usage}
                language={activeLanguage}
                id="usage"
              />
            </div>
          </div>
        </motion.section>

        {/* API Reference */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-20"
        >
          <h2 className="text-3xl font-bold mb-8">API Reference</h2>

          <div className="space-y-8">
            {/* Check Endpoint */}
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-8">
              <div className="mb-4">
                <span className="inline-block px-3 py-1 bg-blue-500/20 text-blue-400 rounded text-sm font-mono mb-2">
                  POST
                </span>
                <h3 className="text-xl font-bold font-mono">/api/v1/sdk/check</h3>
              </div>
              <p className="text-[#8b949e] mb-4">
                Check if a request is allowed based on your budget and rate limits.
              </p>

              <div className="mb-6">
                <h4 className="font-bold mb-2">Request Headers</h4>
                <div className="bg-[#0d1117] border border-[#30363d] rounded p-4 font-mono text-sm">
                  <div className="text-[#8b949e]">
                    X-LLM-Guard-Key: lg_your_api_key
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <h4 className="font-bold mb-2">Request Body</h4>
                <CodeBlock
                  code={`{
  "model": "gpt-4",
  "provider": "openai",
  "estimated_tokens": 1000,
  "request_hash": "sha256-hash",
  "context_count": 0
}`}
                  language="json"
                  id="check-req"
                />
              </div>

              <div>
                <h4 className="font-bold mb-2">Response</h4>
                <CodeBlock
                  code={`{
  "allowed": true,
  "current_spend_usd": 5.50,
  "budget_usd": 10.0,
  "remaining_usd": 4.50,
  "estimated_cost_usd": 0.01
}`}
                  language="json"
                  id="check-res"
                />
              </div>
            </div>

            {/* Report Endpoint */}
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-8">
              <div className="mb-4">
                <span className="inline-block px-3 py-1 bg-green-500/20 text-green-400 rounded text-sm font-mono mb-2">
                  POST
                </span>
                <h3 className="text-xl font-bold font-mono">/api/v1/sdk/report</h3>
              </div>
              <p className="text-[#8b949e] mb-4">
                Report actual usage after calling the LLM API.
              </p>

              <div className="mb-6">
                <h4 className="font-bold mb-2">Request Headers</h4>
                <div className="bg-[#0d1117] border border-[#30363d] rounded p-4 font-mono text-sm">
                  <div className="text-[#8b949e]">
                    X-LLM-Guard-Key: lg_your_api_key
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <h4 className="font-bold mb-2">Request Body</h4>
                <CodeBlock
                  code={`{
  "model": "gpt-4",
  "provider": "openai",
  "input_tokens": 900,
  "output_tokens": 150,
  "cost_usd": 0.01234,
  "latency_ms": 450,
  "is_blocked": false,
  "request_hash": "sha256-hash"
}`}
                  language="json"
                  id="report-req"
                />
              </div>

              <div>
                <h4 className="font-bold mb-2">Response</h4>
                <CodeBlock
                  code={`{
  "received": true
}`}
                  language="json"
                  id="report-res"
                />
              </div>
            </div>
          </div>
        </motion.section>

        {/* Supported Models */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-20"
        >
          <h2 className="text-3xl font-bold mb-8">Supported Models & Providers</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              { provider: 'OpenAI', models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'] },
              {
                provider: 'Anthropic',
                models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
              },
              {
                provider: 'Google',
                models: ['gemini-pro', 'gemini-pro-vision', 'palm-2'],
              },
              { provider: 'Custom', models: ['Any API with token counts'] },
            ].map((item, idx) => (
              <div
                key={idx}
                className="bg-[#161b22] border border-[#30363d] rounded-lg p-6"
              >
                <h3 className="font-bold text-lg mb-3">{item.provider}</h3>
                <ul className="text-[#8b949e] space-y-2">
                  {item.models.map((model, i) => (
                    <li key={i} className="text-sm">
                      • {model}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </motion.section>

        {/* Features */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-20"
        >
          <h2 className="text-3xl font-bold mb-8">Key Features</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: '⏱️',
                title: 'Real-time Tracking',
                desc: 'Monitor API spend in real-time with per-request granularity',
              },
              {
                icon: '🔍',
                title: 'Loop Detection',
                desc: 'Automatic detection of infinite loops and request patterns',
              },
              {
                icon: '🛑',
                title: 'Cost Control',
                desc: 'Set budgets and limits, automatically block requests when exceeded',
              },
              {
                icon: '📊',
                title: 'Analytics',
                desc: 'Detailed analytics and insights into your API usage patterns',
              },
              {
                icon: '🔔',
                title: 'Alerts',
                desc: 'Get notified via Slack or email when thresholds are crossed',
              },
              {
                icon: '⚡',
                title: 'Zero Latency',
                desc: 'Drop-in SDK with minimal performance impact on your app',
              },
            ].map((item, idx) => (
              <div key={idx} className="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
                <div className="text-3xl mb-3">{item.icon}</div>
                <h3 className="font-bold mb-2">{item.title}</h3>
                <p className="text-[#8b949e] text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </motion.section>

        {/* CTA */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-12">
            <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
            <p className="text-[#8b949e] mb-8">
              Sign up for free and get your API key today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/auth/signup">
                <Button className="bg-[#00ff88] text-[#0d1117] font-bold">
                  Create Free Account
                </Button>
              </Link>
              <Link href="/auth/login">
                <Button
                  variant="outline"
                  className="border-[#00ff88]/50 text-[#00ff88]"
                >
                  Already have an account?
                </Button>
              </Link>
            </div>
          </div>
        </motion.section>
      </div>

      {/* Footer */}
      <footer className="bg-[#161b22] border-t border-[#30363d] py-8 px-4">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center text-[#6e7681] text-sm">
          <div>© 2024 LLM Guard.</div>
          <div className="flex gap-6 mt-4 md:mt-0">
            <Link href="/pricing" className="hover:text-[#00ff88]">
              Pricing
            </Link>
            <Link href="/docs" className="hover:text-[#00ff88]">
              Documentation
            </Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
