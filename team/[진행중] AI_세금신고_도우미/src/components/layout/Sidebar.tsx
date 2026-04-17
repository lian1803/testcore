"use client";

import Link from "next/link";
import { FileText } from "lucide-react";
import { SidebarNav } from "./SidebarNav";
import { UserProfile } from "./UserProfile";
import { UsageMeter } from "./UsageMeter";

export function Sidebar() {
  return (
    <aside className="hidden lg:flex flex-col w-64 h-screen bg-white border-r border-[#E2E8F0] fixed left-0 top-0 z-30">
      {/* 로고 */}
      <div className="h-16 flex items-center px-6 border-b border-[#E2E8F0]">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[#1E3A5F] flex items-center justify-center">
            <FileText className="h-4 w-4 text-white" />
          </div>
          <span className="font-bold text-[#1E3A5F]">세금신고 도우미</span>
        </Link>
      </div>

      {/* 네비게이션 */}
      <div className="flex-1 overflow-y-auto py-4">
        <SidebarNav />
      </div>

      {/* 하단 — 사용량 + 유저 프로필 */}
      <div className="pb-4 space-y-3 border-t border-[#E2E8F0] pt-3">
        <UsageMeter />
        <UserProfile />
      </div>
    </aside>
  );
}
