"use client";

import { useState } from "react";
import { Menu, X, FileText } from "lucide-react";
import { SidebarNav } from "./SidebarNav";
import { UsageMeter } from "./UsageMeter";
import { UserProfile } from "./UserProfile";
import Link from "next/link";

interface HeaderBarProps {
  title: string;
  actions?: React.ReactNode;
}

export function HeaderBar({ title, actions }: HeaderBarProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <header className="h-16 bg-white border-b border-[#E2E8F0] flex items-center justify-between px-4 sm:px-6 sticky top-0 z-20">
        {/* 모바일 햄버거 */}
        <div className="flex items-center gap-3">
          <button
            className="lg:hidden p-2 rounded-lg hover:bg-[#F8FAFC]"
            onClick={() => setMobileOpen(true)}
          >
            <Menu className="h-5 w-5 text-[#718096]" />
          </button>
          <h1 className="text-lg font-bold text-[#1A202C]">{title}</h1>
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </header>

      {/* 모바일 사이드 드로어 */}
      {mobileOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/40 z-40 lg:hidden"
            onClick={() => setMobileOpen(false)}
          />
          <div className="fixed left-0 top-0 bottom-0 w-72 bg-white z-50 flex flex-col lg:hidden shadow-xl">
            <div className="h-16 flex items-center justify-between px-4 border-b border-[#E2E8F0]">
              <Link href="/dashboard" className="flex items-center gap-2" onClick={() => setMobileOpen(false)}>
                <div className="w-8 h-8 rounded-lg bg-[#1E3A5F] flex items-center justify-center">
                  <FileText className="h-4 w-4 text-white" />
                </div>
                <span className="font-bold text-[#1E3A5F]">세금신고 도우미</span>
              </Link>
              <button onClick={() => setMobileOpen(false)} className="p-2 rounded-lg hover:bg-[#F8FAFC]">
                <X className="h-5 w-5 text-[#718096]" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto py-4">
              <SidebarNav onNavigate={() => setMobileOpen(false)} />
            </div>
            <div className="pb-4 space-y-3 border-t border-[#E2E8F0] pt-3">
              <UsageMeter />
              <UserProfile />
            </div>
          </div>
        </>
      )}
    </>
  );
}
