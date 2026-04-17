"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { CATEGORY_LABELS } from "@/lib/utils";
import { X } from "lucide-react";

interface Filters {
  category: string;
  dateFrom: string;
  dateTo: string;
}

interface ExpenseFiltersProps {
  filters: Filters;
  onChange: (filters: Filters) => void;
  onReset: () => void;
}

const CATEGORIES = [{ code: "", label: "전체 카테고리" }, ...Object.entries(CATEGORY_LABELS).map(([code, label]) => ({ code, label }))];

export function ExpenseFilters({ filters, onChange, onReset }: ExpenseFiltersProps) {
  const hasFilters = filters.category || filters.dateFrom || filters.dateTo;

  return (
    <div className="flex flex-wrap gap-3 items-center">
      <Select value={filters.category} onValueChange={(v) => onChange({ ...filters, category: v })}>
        <SelectTrigger className="w-44">
          <SelectValue placeholder="카테고리" />
        </SelectTrigger>
        <SelectContent>
          {CATEGORIES.map((c) => (
            <SelectItem key={c.code} value={c.code}>{c.label}</SelectItem>
          ))}
        </SelectContent>
      </Select>

      <div className="flex items-center gap-2">
        <Input
          type="date"
          value={filters.dateFrom}
          onChange={(e) => onChange({ ...filters, dateFrom: e.target.value })}
          className="w-36"
        />
        <span className="text-[#718096] text-sm">~</span>
        <Input
          type="date"
          value={filters.dateTo}
          onChange={(e) => onChange({ ...filters, dateTo: e.target.value })}
          className="w-36"
        />
      </div>

      {hasFilters && (
        <Button variant="ghost" size="sm" onClick={onReset} className="gap-1.5">
          <X className="h-3.5 w-3.5" />
          초기화
        </Button>
      )}
    </div>
  );
}
