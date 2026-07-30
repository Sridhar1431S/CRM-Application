import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, LayoutDashboard, ShieldCheck, Users } from "lucide-react";
import { Button } from "@/components/ui/button";

type RoleSelection = "admin" | "sales_rep";

export default function LandingPage() {
  const navigate = useNavigate();
  const [showRoleOptions, setShowRoleOptions] = useState(false);

  const handleSelectRole = (role: RoleSelection) => {
    navigate("/login", { state: { role } });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top_left,_rgba(51,88,244,0.16),_transparent_40%),linear-gradient(135deg,_#f7f8fb_0%,_#eef2ff_100%)] px-4 py-10 transition-all duration-300 dark:bg-[radial-gradient(circle_at_top_left,_rgba(51,88,244,0.24),_transparent_35%),linear-gradient(135deg,_#020617_0%,_#0f172a_100%)]">
      <div className="w-full max-w-5xl overflow-hidden rounded-[1.5rem] border border-border bg-surface/90 shadow-[var(--shadow-popover)] backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_24px_60px_rgba(15,23,42,0.16)]">
        <div className="grid gap-0 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="p-8 sm:p-10 lg:p-12">
            <div className="mb-6 inline-flex items-center rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-sm font-medium text-brand-700 dark:border-brand-900 dark:bg-brand-950/40 dark:text-brand-300">
              <ShieldCheck className="mr-2 h-4 w-4" />
              Modern CRM operations for growing teams
            </div>
            <h1 className="text-4xl font-semibold tracking-tight text-ink-900 sm:text-5xl">
              Run your pipeline with clarity.
            </h1>
            <p className="mt-4 max-w-xl text-lg text-ink-500">
              Track customers, leads, opportunities, and follow-ups from one elegant workspace built for modern sales teams.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              {!showRoleOptions ? (
                <>
                  <Button size="lg" onClick={() => setShowRoleOptions(true)} className="animate-[fadeIn_0.3s_ease-out]">
                    Get Started
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                  <Button size="lg" variant="secondary">
                    <LayoutDashboard className="h-4 w-4" />
                    View Dashboard
                  </Button>
                  <Button size="lg" variant="ghost">
                    <Users className="h-4 w-4" />
                    Meet the Team
                  </Button>
                </>
              ) : (
                <div className="w-full space-y-3">
                  <p className="text-sm font-medium text-ink-500">Choose your access path</p>
                  <Button size="lg" className="w-full transition-transform duration-200 hover:-translate-y-0.5" onClick={() => handleSelectRole("admin")}>
                    Continue as Admin
                  </Button>
                  <Button size="lg" variant="secondary" className="w-full transition-transform duration-200 hover:-translate-y-0.5" onClick={() => handleSelectRole("sales_rep")}>
                    Continue as Sales Rep
                  </Button>
                  <Button size="lg" variant="ghost" className="w-full" onClick={() => setShowRoleOptions(false)}>
                    Back
                  </Button>
                </div>
              )}
            </div>
          </div>

          <div className="border-t border-border bg-canvas/70 p-8 sm:p-10 lg:border-l lg:border-t-0">
            <div className="rounded-[1rem] border border-border bg-surface p-6 shadow-[var(--shadow-card)]">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-ink-500">What you can do</p>
              <ul className="mt-4 space-y-3 text-sm text-ink-600">
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-2.5 w-2.5 rounded-full bg-brand-600" />
                  Monitor opportunity progress at a glance.
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-2.5 w-2.5 rounded-full bg-brand-600" />
                  Keep follow-ups organized and timely.
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-2.5 w-2.5 rounded-full bg-brand-600" />
                  Access insights for both admins and sales reps.
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
