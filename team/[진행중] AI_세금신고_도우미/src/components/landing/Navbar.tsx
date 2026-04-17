"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { FileText, Menu, X } from "lucide-react";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", handler);
    return () => window.removeEventListener("scroll", handler);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 h-16 flex items-center transition-all duration-200 ${
        scrolled ? "bg-white/95 backdrop-blur-md shadow-sm border-b border-[#E2E8F0]" : "bg-transparent"
      }`}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 w-full flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[#1E3A5F] flex items-center justify-center">
            <FileText className="h-4 w-4 text-white" />
          </div>
          <span className="font-bold text-[#1E3A5F] text-lg">세금신고 도우미</span>
        </Link>

        <div className="hidden md:flex items-center gap-3">
          <Link href="/login">
            <Button variant="ghost" size="sm">로그인</Button>
          </Link>
          <Link href="/signup">
            <Button variant="accent" size="sm">무료로 시작하기</Button>
          </Link>
        </div>

        <button
          className="md:hidden p-2 rounded-lg hover:bg-gray-100"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {mobileOpen && (
        <div className="absolute top-16 left-0 right-0 bg-white border-b border-[#E2E8F0] shadow-lg p-4 flex flex-col gap-3 md:hidden">
          <Link href="/login" onClick={() => setMobileOpen(false)}>
            <Button variant="ghost" className="w-full">로그인</Button>
          </Link>
          <Link href="/signup" onClick={() => setMobileOpen(false)}>
            <Button variant="accent" className="w-full">무료로 시작하기</Button>
          </Link>
        </div>
      )}
    </nav>
  );
}
