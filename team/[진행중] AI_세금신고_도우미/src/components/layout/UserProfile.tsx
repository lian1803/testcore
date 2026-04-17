"use client";

import { useAuthStore } from "@/store/auth.store";
import { LogOut, Settings } from "lucide-react";
import Link from "next/link";

export function UserProfile() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  if (!user) return null;

  const initials = user.name
    ? user.name.slice(0, 2)
    : user.email.slice(0, 2).toUpperCase();

  return (
    <div className="flex items-center gap-3 px-3 py-2 mx-3 rounded-xl hover:bg-[#F8FAFC] group">
      <div className="w-9 h-9 rounded-full bg-[#1E3A5F] flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
        {initials}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-[#1A202C] truncate">{user.name}</p>
        <p className="text-xs text-[#718096] truncate">{user.email}</p>
      </div>
      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Link href="/dashboard/settings" className="p-1 rounded hover:bg-[#E2E8F0]">
          <Settings className="h-4 w-4 text-[#718096]" />
        </Link>
        <button onClick={logout} className="p-1 rounded hover:bg-[#E2E8F0]">
          <LogOut className="h-4 w-4 text-[#718096]" />
        </button>
      </div>
    </div>
  );
}
