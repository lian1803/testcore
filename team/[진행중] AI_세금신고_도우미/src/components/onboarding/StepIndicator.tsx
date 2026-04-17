import { Progress } from "@/components/ui/progress";
import { Check } from "lucide-react";

interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

const STEP_LABELS = ["업종 선택", "사업자 정보", "신고 연도"];

export function StepIndicator({ currentStep, totalSteps }: StepIndicatorProps) {
  const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-3">
        {STEP_LABELS.map((label, index) => {
          const stepNum = index + 1;
          const isCompleted = stepNum < currentStep;
          const isCurrent = stepNum === currentStep;
          return (
            <div key={label} className="flex flex-col items-center gap-1">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                  isCompleted
                    ? "bg-[#1E3A5F] text-white"
                    : isCurrent
                    ? "bg-[#2D5F8A] text-white"
                    : "bg-[#E2E8F0] text-[#718096]"
                }`}
              >
                {isCompleted ? <Check className="h-4 w-4" /> : stepNum}
              </div>
              <span className={`text-xs font-medium ${isCurrent ? "text-[#1E3A5F]" : "text-[#718096]"}`}>
                {label}
              </span>
            </div>
          );
        })}
      </div>
      <Progress value={progress} className="h-2" />
      <p className="text-right text-xs text-[#718096] mt-1">{currentStep}/{totalSteps}</p>
    </div>
  );
}
