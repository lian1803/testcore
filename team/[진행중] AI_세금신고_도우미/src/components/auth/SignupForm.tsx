"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PasswordInput } from "./PasswordInput";
import { SocialLoginButtons } from "./SocialLoginButtons";

interface FormState {
  name: string;
  email: string;
  password: string;
  agreeTerms: boolean;
}

interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
  agreeTerms?: string;
  general?: string;
}

export function SignupForm() {
  const router = useRouter();
  const [form, setForm] = useState<FormState>({
    name: "",
    email: "",
    password: "",
    agreeTerms: false,
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);

  const validate = (): boolean => {
    const errs: FormErrors = {};
    if (!form.name.trim()) errs.name = "이름을 입력해주세요";
    if (!form.email) errs.email = "이메일을 입력해주세요";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = "올바른 이메일 형식이 아닙니다";
    if (!form.password) errs.password = "비밀번호를 입력해주세요";
    else if (form.password.length < 8) errs.password = "비밀번호는 8자 이상이어야 합니다";
    else if (!/[!@#$%^&*(),.?":{}|<>]/.test(form.password)) errs.password = "특수문자를 포함해야 합니다";
    if (!form.agreeTerms) errs.agreeTerms = "이용약관에 동의해주세요";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: form.name, email: form.email, password: form.password }),
      });

      if (!res.ok) {
        const data = await res.json();
        setErrors({ general: data.message || "회원가입에 실패했습니다" });
        return;
      }

      router.push("/onboarding");
    } catch {
      setErrors({ general: "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8 border border-[#E2E8F0]">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-[#1A202C] mb-2">무료로 시작하세요</h1>
        <p className="text-[#718096] text-sm">신용카드 불필요 · 영수증 20건 무료</p>
      </div>

      <SocialLoginButtons />

      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-[#E2E8F0]" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="bg-white px-3 text-[#718096]">또는 이메일로 계속하기</span>
        </div>
      </div>

      {errors.general && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
          {errors.general}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="name">이름</Label>
          <Input
            id="name"
            placeholder="홍길동"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            onBlur={validate}
            error={!!errors.name}
            autoComplete="name"
          />
          {errors.name && <p className="text-xs text-[#EF4444]">{errors.name}</p>}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="email">이메일 주소</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            onBlur={validate}
            error={!!errors.email}
            autoComplete="email"
          />
          {errors.email && <p className="text-xs text-[#EF4444]">{errors.email}</p>}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="password">비밀번호</Label>
          <PasswordInput
            id="password"
            placeholder="8자 이상, 특수문자 포함"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            onBlur={validate}
            error={!!errors.password}
            autoComplete="new-password"
          />
          {errors.password && <p className="text-xs text-[#EF4444]">{errors.password}</p>}
        </div>

        <div className="space-y-1.5">
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={form.agreeTerms}
              onChange={(e) => setForm({ ...form, agreeTerms: e.target.checked })}
              className="mt-0.5 h-4 w-4 rounded border-[#E2E8F0] accent-[#1E3A5F]"
            />
            <span className="text-sm text-[#1A202C]">
              <Link href="#" className="text-[#1E3A5F] hover:underline">이용약관</Link> 및{" "}
              <Link href="#" className="text-[#1E3A5F] hover:underline">개인정보처리방침</Link>에 동의합니다
            </span>
          </label>
          {errors.agreeTerms && <p className="text-xs text-[#EF4444]">{errors.agreeTerms}</p>}
        </div>

        <Button type="submit" className="w-full" size="lg" loading={loading}>
          회원가입하기
        </Button>
      </form>

      <p className="text-center text-sm text-[#718096] mt-6">
        이미 계정이 있으신가요?{" "}
        <Link href="/login" className="text-[#1E3A5F] font-medium hover:underline">
          로그인
        </Link>
      </p>
    </div>
  );
}
