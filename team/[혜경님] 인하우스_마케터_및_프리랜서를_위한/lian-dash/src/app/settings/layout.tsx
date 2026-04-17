"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { Plug, CreditCard, User } from "lucide-react";
import { cn } from "@/lib/utils";

/* ─── Settings Nav ───────────────────────────────────── */
const settingsNav = [
  { href: "/settings/integrations", icon: Plug, label: "채널 연동" },
  { href: "/settings/billing", icon: CreditCard, label: "결제" },
  { href: "/settings/account", icon: User, label: "계정" },
];

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen flex" style={{ background: "var(--bg-base)", color: "var(--text-primary)" }}>
      {/* ── Sidebar Nav ─────────────────────────────────── */}
      <aside className="w-52 border-r p-6 shrink-0" style={{ background: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}>
        <h2 className="text-sm font-bold text-white mb-6">설정</h2>
        <nav className="space-y-1">
          {settingsNav.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-lg transition-all relative group",
                  isActive
                    ? "text-white"
                    : "text-zinc-500 hover:text-zinc-300"
                )}
              >
                <item.icon className="w-4 h-4 shrink-0" />
                <span className="text-sm font-medium">{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="settings-active"
                    className="absolute inset-0 rounded-lg border border-white/20 pointer-events-none"
                    style={{ background: "rgba(255,255,255,0.05)" }}
                  />
                )}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* ── Main Content ────────────────────────────────── */}
      <main className="flex-1 overflow-auto">
        <div className="px-8 py-8 max-w-4xl">
          {children}
        </div>
      </main>
    </div>
  );
}
