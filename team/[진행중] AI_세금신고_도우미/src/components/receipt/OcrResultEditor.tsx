"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CATEGORY_LABELS } from "@/lib/utils";
import type { ExpenseCategory } from "@/lib/mock-data";
import { AlertCircle, CheckCircle2 } from "lucide-react";

interface OcrResult {
  merchantName: string;
  date: string;
  amount: number;
  category: ExpenseCategory;
  confidence: number;
  lowConfidenceFields: string[];
  classificationReason: string;
}

interface OcrResultEditorProps {
  result: OcrResult;
  onSave: (data: OcrResult & { isBusinessExpense: boolean; memo: string }) => void;
  onCancel: () => void;
  saving?: boolean;
}

const CATEGORIES = Object.entries(CATEGORY_LABELS) as [ExpenseCategory, string][];

export function OcrResultEditor({ result, onSave, onCancel, saving }: OcrResultEditorProps) {
  const [form, setForm] = useState({
    merchantName: result.merchantName,
    date: result.date,
    amount: String(result.amount),
    category: result.category,
    isBusinessExpense: true,
    memo: "",
  });

  const isLowConfidence = (field: string) => result.lowConfidenceFields.includes(field);

  const handleSave = () => {
    onSave({
      ...result,
      merchantName: form.merchantName,
      date: form.date,
      amount: Number(form.amount.replace(/,/g, "")),
      category: form.category,
      isBusinessExpense: form.isBusinessExpense,
      memo: form.memo,
    });
  };

  return (
    <div className="space-y-6">
      {/* AI 분류 결과 헤더 */}
      <div className="p-4 bg-[#22C55E]/10 border border-[#22C55E]/20 rounded-xl flex gap-3">
        <CheckCircle2 className="h-5 w-5 text-[#22C55E] flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-[#166534]">AI 분류 완료 (신뢰도 {Math.round(result.confidence * 100)}%)</p>
          <p className="text-xs text-[#166534]/70 mt-0.5">{result.classificationReason}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* 상호명 */}
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <Label htmlFor="merchantName">상호명</Label>
            {isLowConfidence("merchantName") && (
              <Badge variant="warning" className="text-xs gap-1">
                <AlertCircle className="h-3 w-3" /> 확인 필요
              </Badge>
            )}
          </div>
          <Input
            id="merchantName"
            value={form.merchantName}
            onChange={(e) => setForm({ ...form, merchantName: e.target.value })}
            className={isLowConfidence("merchantName") ? "bg-[#FEF3C7]/30" : ""}
          />
        </div>

        {/* 날짜 */}
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <Label htmlFor="date">날짜</Label>
            {isLowConfidence("date") && (
              <Badge variant="warning" className="text-xs gap-1">
                <AlertCircle className="h-3 w-3" /> 확인 필요
              </Badge>
            )}
          </div>
          <Input
            id="date"
            type="date"
            value={form.date}
            onChange={(e) => setForm({ ...form, date: e.target.value })}
            className={isLowConfidence("date") ? "bg-[#FEF3C7]/30" : ""}
          />
        </div>

        {/* 금액 */}
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <Label htmlFor="amount">금액 (원)</Label>
            {isLowConfidence("amount") && (
              <Badge variant="warning" className="text-xs gap-1">
                <AlertCircle className="h-3 w-3" /> 확인 필요
              </Badge>
            )}
          </div>
          <div className="relative">
            <Input
              id="amount"
              value={Number(form.amount.replace(/,/g, "")).toLocaleString("ko-KR")}
              onChange={(e) => {
                const raw = e.target.value.replace(/,/g, "");
                if (/^\d*$/.test(raw)) setForm({ ...form, amount: raw });
              }}
              className={isLowConfidence("amount") ? "bg-[#FEF3C7]/30 pr-8" : "pr-8"}
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-[#718096]">원</span>
          </div>
        </div>

        {/* 카테고리 */}
        <div className="space-y-1.5">
          <Label>경비 분류</Label>
          <Select value={form.category} onValueChange={(v) => setForm({ ...form, category: v as ExpenseCategory })}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {CATEGORIES.map(([code, label]) => (
                <SelectItem key={code} value={code}>{label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* 사업 관련 여부 */}
      <div className="flex items-center justify-between p-4 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
        <div>
          <p className="text-sm font-medium text-[#1A202C]">사업 관련 경비</p>
          <p className="text-xs text-[#718096]">업무와 직접 관련된 경비만 공제됩니다</p>
        </div>
        <Switch
          checked={form.isBusinessExpense}
          onCheckedChange={(checked) => setForm({ ...form, isBusinessExpense: checked })}
        />
      </div>

      {/* 메모 */}
      <div className="space-y-1.5">
        <Label htmlFor="memo">메모 (선택)</Label>
        <textarea
          id="memo"
          value={form.memo}
          onChange={(e) => setForm({ ...form, memo: e.target.value })}
          placeholder="클라이언트 미팅, 출장 등 용도를 기록하면 나중에 확인하기 좋아요"
          rows={2}
          className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] text-sm text-[#1A202C] placeholder:text-[#718096] focus:outline-none focus:ring-2 focus:ring-[#1E3A5F] resize-none"
        />
      </div>

      <div className="flex gap-3">
        <Button variant="outline" onClick={onCancel} className="flex-1">
          취소
        </Button>
        <Button variant="accent" onClick={handleSave} className="flex-1" loading={saving}>
          저장하기
        </Button>
      </div>
    </div>
  );
}
