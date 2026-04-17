import { Sidebar } from "@/components/layout/Sidebar";
import { LegalBanner } from "@/components/common/LegalBanner";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <div className="lg:pl-64 flex flex-col min-h-screen">
        <LegalBanner />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
