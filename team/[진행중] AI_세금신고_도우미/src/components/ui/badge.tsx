import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-[#1E3A5F] text-white",
        accent: "bg-[#22C55E] text-white",
        secondary: "bg-[#F1F5F9] text-[#475569]",
        outline: "border border-[#E2E8F0] text-[#1A202C]",
        warning: "bg-[#FEF3C7] text-[#92400E]",
        error: "bg-red-100 text-red-700",
        meal: "bg-[#FEF3C7] text-[#92400E]",
        transportation: "bg-[#DBEAFE] text-[#1E40AF]",
        communication: "bg-[#F3E8FF] text-[#6B21A8]",
        office: "bg-[#DCFCE7] text-[#166534]",
        education: "bg-[#FFE4E6] text-[#9F1239]",
        other: "bg-[#F1F5F9] text-[#475569]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
