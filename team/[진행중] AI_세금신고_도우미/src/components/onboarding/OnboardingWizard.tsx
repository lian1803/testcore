"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { StepIndicator } from "./StepIndicator";
import { Step1BusinessType } from "./Step1BusinessType";
import { Step2TaxationType } from "./Step2TaxationType";
import { Step3TaxYear } from "./Step3TaxYear";
import { ArrowLeft, ArrowRight } from "lucide-react";

interface WizardState {
  businessType: string;
  taxationType: string;
  registrationNumber: string;
  taxYear: string;
}

interface WizardErrors {
  businessType?: string;
  taxationType?: string;
  taxYear?: string;
}

const TOTAL_STEPS = 3;

export function OnboardingWizard() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [state, setState] = useState<WizardState>({
    businessType: "",
    taxationType: "",
    registrationNumber: "",
    taxYear: String(new Date().getFullYear() - 1),
  });
  const [errors, setErrors] = useState<WizardErrors>({});

  const validateStep = (step: number): boolean => {
    const errs: WizardErrors = {};
    if (step === 1 && !state.businessType) errs.businessType = "업종을 선택해주세요";
    if (step === 2 && !state.taxationType) errs.taxationType = "과세 유형을 선택해주세요";
    if (step === 3 && !state.taxYear) errs.taxYear = "신고 연도를 선택해주세요";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleNext = () => {
    if (!validateStep(currentStep)) return;
    if (currentStep < TOTAL_STEPS) {
      setCurrentStep((prev) => prev + 1);
      setErrors({});
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
      setErrors({});
    }
  };

  const handleFinish = async () => {
    if (!validateStep(currentStep)) return;
    setSubmitting(true);
    try {
      await fetch("/api/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          businessType: state.businessType,
          taxationType: state.taxationType,
          registrationNumber: state.registrationNumber || null,
          taxYear: Number(state.taxYear),
        }),
      });
      router.push("/dashboard");
    } catch {
      // 오류 발생 시에도 대시보드로 이동 (mock 환경 대응)
      router.push("/dashboard");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8 border border-[#E2E8F0] w-full max-w-lg mx-auto">
      <StepIndicator currentStep={currentStep} totalSteps={TOTAL_STEPS} />

      <div className="min-h-[320px]">
        {currentStep === 1 && (
          <Step1BusinessType
            value={state.businessType}
            onChange={(val) => setState({ ...state, businessType: val })}
            error={errors.businessType}
          />
        )}
        {currentStep === 2 && (
          <Step2TaxationType
            taxationType={state.taxationType}
            registrationNumber={state.registrationNumber}
            onTaxationTypeChange={(val) => setState({ ...state, taxationType: val })}
            onRegistrationNumberChange={(val) => setState({ ...state, registrationNumber: val })}
            error={errors.taxationType}
          />
        )}
        {currentStep === 3 && (
          <Step3TaxYear
            taxYear={state.taxYear}
            onChange={(val) => setState({ ...state, taxYear: val })}
            error={errors.taxYear}
          />
        )}
      </div>

      <div className="flex items-center justify-between mt-8 pt-6 border-t border-[#E2E8F0]">
        <Button
          variant="ghost"
          onClick={handleBack}
          disabled={currentStep === 1}
          className="gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          이전
        </Button>

        {currentStep < TOTAL_STEPS ? (
          <Button onClick={handleNext} className="gap-2">
            다음
            <ArrowRight className="h-4 w-4" />
          </Button>
        ) : (
          <Button onClick={handleFinish} variant="accent" className="gap-2" loading={submitting}>
            시작하기
            <ArrowRight className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
