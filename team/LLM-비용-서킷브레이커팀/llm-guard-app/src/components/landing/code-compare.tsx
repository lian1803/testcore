'use client';

import { motion } from 'framer-motion';

export function CodeCompare() {
  return (
    <div className="flex flex-col md:flex-row gap-8 items-center justify-center w-full">
      {/* BEFORE */}
      <motion.div
        initial={{ opacity: 0, x: -40 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true, margin: '-100px' }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="flex-1 bg-[#161b22] rounded-lg p-6 border border-[#30363d] relative overflow-hidden group"
      >
        <div className="absolute inset-0 bg-[#ff4444] opacity-0 group-hover:opacity-5 transition-opacity duration-300" />
        <div className="relative z-10">
          <div className="text-sm text-[#8b949e] mb-4 font-semibold">BEFORE (Unprotected)</div>
          <pre className="text-xs font-mono text-[#e6edf3] overflow-x-auto">
            <code>{`from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
  model="gpt-4",
  messages=[{"role": "user", 
             "content": "..."}]
)
# 🚨 $72,000 bill incoming
# Agent loop × 10,000 calls`}</code>
          </pre>
          <div className="mt-4 inline-block px-3 py-1 bg-[#ff4444]/20 text-[#ff4444] rounded text-xs font-semibold">
            ✗ Unguarded
          </div>
        </div>
      </motion.div>

      {/* AFTER */}
      <motion.div
        initial={{ opacity: 0, x: 40 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true, margin: '-100px' }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="flex-1 bg-[#161b22] rounded-lg p-6 border border-[#00ff88]/30 relative overflow-hidden group"
        style={{
          boxShadow: '0 0 20px rgba(0, 255, 136, 0.2)',
        }}
      >
        <div className="absolute inset-0 bg-[#00ff88] opacity-0 group-hover:opacity-5 transition-opacity duration-300" />
        <div className="relative z-10">
          <div className="text-sm text-[#00ff88] mb-4 font-semibold">AFTER (Protected)</div>
          <pre className="text-xs font-mono text-[#e6edf3] overflow-x-auto">
            <code>{`from llm_guard.openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
  model="gpt-4",
  messages=[{"role": "user", 
             "content": "..."}]
)
# ✓ Loop detected
# ✓ Request blocked
# ✓ Alert sent`}</code>
          </pre>
          <div className="mt-4 inline-block px-3 py-1 bg-[#00ff88]/20 text-[#00ff88] rounded text-xs font-semibold">
            ✓ Guarded
          </div>
        </div>
      </motion.div>
    </div>
  );
}
