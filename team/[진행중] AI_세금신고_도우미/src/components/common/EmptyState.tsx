import { Button } from "@/components/ui/button";
import { LucideIcon } from "lucide-react";
import Link from "next/link";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  cta?: { label: string; href: string };
}

export function EmptyState({ icon: Icon, title, description, cta }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4 text-center">
      <div className="w-16 h-16 rounded-2xl bg-[#F1F5F9] flex items-center justify-center">
        <Icon className="h-8 w-8 text-[#718096]" />
      </div>
      <div>
        <h3 className="text-base font-semibold text-[#1A202C] mb-1">{title}</h3>
        <p className="text-sm text-[#718096] max-w-xs">{description}</p>
      </div>
      {cta && (
        <Link href={cta.href}>
          <Button variant="accent">{cta.label}</Button>
        </Link>
      )}
    </div>
  );
}
