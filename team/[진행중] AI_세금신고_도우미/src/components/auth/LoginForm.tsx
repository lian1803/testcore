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
  email: string;
  password: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

export function LoginForm() {
  const router = useRouter();
  const [form, setForm] = useState<FormState>({ email: "", password: "" });
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);

  const validate = (): boolean => {
    const errs: FormErrors = {};
    if (!form.email) errs.email = "이메일을 입력해주세요";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = "올바른 이메일 형식이 아닙니다";
    if (!form.password) errs.password = "비밀번호를 입력해주세요";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleBlur = (field: keyof FormState) => {
    validate();
    void field;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        const data = await res.json();
        setErrors({ general: data.message || "로그인에 실패했습니다" });
        return;
      }

      router.push("/dashboard");
    } catch {
      setErrors({ general: "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8 border border-[#E2E8F0]">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-[#1A202C] mb-2">다시 오셨네요</h1>
        <p className="text-[#718096] text-sm">로그인하여 경비 관리를 계속하세요</p>
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
          <Label htmlFor="email">이메일 주소</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            onBlur={() => handleBlur("email")}
            error={!!errors.email}
            autoComplete="email"
          />
          {errors.email && <p className="text-xs text-[#EF4444]">{errors.email}</p>}
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="password">비밀번호</Label>
            <Link href="#" className="text-xs text-[#1E3A5F] hover:underline">
              비밀번호를 잊으셨나요?
            </Link>
          </div>
          <PasswordInput
            id="password"
            placeholder="비밀번호 입력"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            onBlur={() => handleBlur("password")}
            error={!!errors.password}
            autoComplete="current-password"
          />
          {errors.password && <p className="text-xs text-[#EF4444]">{errors.password}</p>}
        </div>

        <Button type="submit" className="w-full" size="lg" loading={loading}>
          로그인
        </Button>
      </form>

      <p className="text-center text-sm text-[#718096] mt-6">
        계정이 없으신가요?{" "}
        <Link href="/signup" className="text-[#1E3A5F] font-medium hover:underline">
          무료로 시작하기
        </Link>
      </p>
    </div>
  );
}
