"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Zap, LayoutDashboard, BarChart3, Brain,
  Settings, BookOpen, HelpCircle,
  ChevronRight, ArrowUpRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

/* ─── Nav ────────────────────────────────────────────── */
const navItems = [
  { href: "/dashboard",           icon: LayoutDashboard, label: "개요",        labelEn: "Overview" },
  { href: "/dashboard/ga4",       icon: BarChart3,        label: "GA4",         labelEn: "GA4" },
  { href: "/dashboard/meta",      icon: BarChart3,        label: "메타",        labelEn: "Meta" },
  { href: "/dashboard/naver",     icon: BarChart3,        label: "네이버SA",    labelEn: "Naver" },
  { href: "/dashboard/insights",  icon: Brain,            label: "AI 인사이트", labelEn: "Insights" },
  { href: "/settings/integrations", icon: Settings,      label: "설정",        labelEn: "Settings" },
];

const workspaces = [
  { name: "자사 워크스페이스", initial: "자", color: "#5b6cf9" },
  { name: "클라이언트 A",     initial: "A",  color: "#E37400" },
];

/* ─── Sidebar ────────────────────────────────────────── */
function Sidebar() {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState(true);
  const [wsOpen, setWsOpen]   = useState(false);
  const [activeWs, setActiveWs] = useState(0);

  return (
    <motion.aside
      animate={{ width: expanded ? 240 : 64 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="h-screen fixed left-0 top-0 z-40 flex flex-col border-r overflow-hidden shrink-0"
      style={{
        background: "var(--bg-surface)",
        borderColor: "var(--border-subtle)",
      }}
    >
      {/* Logo + collapse */}
      <div className="flex items-center justify-between px-4 py-5 shrink-0">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-7 h-7 bg-white rounded-lg flex items-center justify-center shrink-0">
            <Zap className="w-4 h-4 text-black" />
          </div>
          <AnimatePresence>
            {expanded && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "auto" }}
                exit={{ opacity: 0, width: 0 }}
                className="font-bold text-white tracking-tight text-sm whitespace-nowrap overflow-hidden">
                Lian Dash
              </motion.span>
            )}
          </AnimatePresence>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-6 h-6 rounded-md flex items-center justify-center text-zinc-600 hover:text-zinc-300 hover:bg-white/6 transition-all shrink-0"
        >
          <ChevronRight className={cn("w-3.5 h-3.5 transition-transform", expanded && "rotate-180")} />
        </button>
      </div>

      {/* Workspace selector */}
      <div className="px-3 mb-4 shrink-0">
        <button
          onClick={() => setWsOpen(!wsOpen)}
          className={cn(
            "w-full flex items-center gap-2.5 px-2 py-2.5 rounded-lg transition-all",
            "border border-white/7 hover:border-white/12 hover:bg-white/5"
          )}
        >
          <div className="w-6 h-6 rounded-md flex items-center justify-center text-[10px] font-bold text-white shrink-0"
            style={{ background: workspaces[activeWs].color }}>
            {workspaces[activeWs].initial}
          </div>
          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="flex-1 min-w-0 text-left">
                <p className="text-xs font-semibold text-white truncate">{workspaces[activeWs].name}</p>
                <p className="text-[9px] text-zinc-500 font-mono uppercase tracking-wider">Pro Plan</p>
              </motion.div>
            )}
          </AnimatePresence>
        </button>

        {/* Workspace dropdown */}
        <AnimatePresence>
          {wsOpen && expanded && (
            <motion.div
              initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }}
              className="mt-1 rounded-lg border border-white/8 overflow-hidden"
              style={{ background: "var(--bg-elevated)" }}>
              {workspaces.map((ws, i) => (
                <button key={ws.name}
                  onClick={() => { setActiveWs(i); setWsOpen(false); }}
                  className={cn(
                    "w-full flex items-center gap-2.5 px-3 py-2.5 text-left transition-colors hover:bg-white/5",
                    i === activeWs && "bg-white/5"
                  )}>
                  <div className="w-5 h-5 rounded flex items-center justify-center text-[9px] font-bold text-white shrink-0"
                    style={{ background: ws.color }}>
                    {ws.initial}
                  </div>
                  <span className="text-xs text-zinc-300 truncate">{ws.name}</span>
                  {i === activeWs && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-white shrink-0" />}
                </button>
              ))}
              <div className="border-t border-white/6">
                <button className="w-full flex items-center gap-2 px-3 py-2.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors">
                  <span className="text-lg leading-none">+</span> 워크스페이스 추가
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-3 space-y-0.5 overflow-y-auto overflow-x-hidden">
        {navItems.map((item) => {
          const isActive = item.href === "/dashboard"
            ? pathname === "/dashboard"
            : pathname.startsWith(item.href);

          return (
            <Link key={item.href} href={item.href}
              className={cn(
                "sidebar-item group",
                isActive && "active"
              )}>
              <item.icon className={cn(
                "w-4 h-4 shrink-0 transition-colors",
                isActive ? "text-white" : "text-zinc-500 group-hover:text-zinc-300"
              )} />
              <AnimatePresence>
                {expanded && (
                  <motion.span
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="whitespace-nowrap overflow-hidden text-ellipsis">
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
              {isActive && (
                <motion.div
                  layoutId="active-indicator"
                  className="ml-auto w-1 h-4 rounded-full bg-white shrink-0"
                />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="border-t px-3 py-4 space-y-1 shrink-0" style={{ borderColor: "var(--border-subtle)" }}>
        <Link href="#" className="sidebar-item">
          <BookOpen className="w-4 h-4 text-zinc-500 shrink-0" />
          <AnimatePresence>
            {expanded && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="whitespace-nowrap">문서</motion.span>
            )}
          </AnimatePresence>
        </Link>
        <Link href="#" className="sidebar-item">
          <HelpCircle className="w-4 h-4 text-zinc-500 shrink-0" />
          <AnimatePresence>
            {expanded && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="whitespace-nowrap">고객지원</motion.span>
            )}
          </AnimatePresence>
        </Link>

        {/* Upgrade CTA */}
        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="mt-3 p-3 rounded-xl border border-white/8 relative overflow-hidden"
              style={{ background: "rgba(255,255,255,0.04)" }}>
              <p className="text-xs font-bold text-white mb-0.5">에이전시 플랜</p>
              <p className="text-[10px] text-zinc-500 mb-3">무제한 워크스페이스 잠금 해제</p>
              <button className="flex items-center gap-1 text-xs font-semibold text-white hover:text-zinc-300 transition-colors">
                업그레이드 <ArrowUpRight className="w-3 h-3" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* User avatar */}
        <div className={cn("flex items-center gap-2.5 px-2 py-2 mt-1 rounded-lg hover:bg-white/5 transition-colors cursor-pointer", !expanded && "justify-center")}>
          <div className="w-7 h-7 rounded-full bg-zinc-700 flex items-center justify-center text-xs font-bold text-white shrink-0">
            홍
          </div>
          <AnimatePresence>
            {expanded && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <p className="text-xs font-semibold text-white whitespace-nowrap">홍길동</p>
                <p className="text-[9px] text-zinc-500 whitespace-nowrap">hong@company.com</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.aside>
  );
}

/* ─── Layout ─────────────────────────────────────────── */
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen" style={{ background: "var(--bg-base)" }}>
      <Sidebar />
      {/* The main area uses a left margin animated by the sidebar width.
          We use a simpler approach: just use ml with a static value,
          since the sidebar default is 240px. */}
      <main className="flex-1 min-h-screen overflow-auto" style={{ marginLeft: 240, transition: "margin-left 0.3s cubic-bezier(0.16,1,0.3,1)" }}>
        {children}
      </main>
    </div>
  );
}
