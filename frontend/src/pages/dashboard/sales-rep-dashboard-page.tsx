import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Users, Target, TrendingUp, CalendarClock } from "lucide-react";
import { dashboardApi } from "@/api/dashboard";
import { followupsApi } from "@/api/followups";
import { KpiCard } from "@/components/shared/kpi-card";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";

export default function SalesRepDashboardPage() {
  const user = useAuthStore((s) => s.user);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["dashboard", "sales-rep"],
    queryFn: dashboardApi.salesRep,
  });

  const {
    data: upcoming,
    isLoading: upcomingLoading,
    isError: upcomingIsError,
    error: upcomingError,
    refetch: refetchUpcoming,
  } = useQuery({
    queryKey: ["followups", "upcoming"],
    queryFn: followupsApi.upcoming,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-ink-900">Welcome back, {user?.name?.split(" ")[0]}</h2>
        <p className="text-sm text-ink-500">Here's what's on your plate today.</p>
      </div>

      {isError && (
        <Card>
          <ErrorState title="Couldn't load your dashboard" error={error} onRetry={() => refetch()} />
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-[92px] rounded-[var(--radius-card)]" />)
        ) : (
          <>
            <KpiCard label="Assigned Customers" value={data?.assigned_customers ?? 0} icon={Users} tone="brand" />
            <KpiCard label="Assigned Leads" value={data?.assigned_leads ?? 0} icon={Target} tone="info" />
            <KpiCard label="Open Opportunities" value={data?.open_opportunities ?? 0} icon={TrendingUp} tone="warning" />
            <KpiCard
              label="Follow-ups Due Today"
              value={data?.followups_due_today ?? 0}
              icon={CalendarClock}
              tone="success"
            />
          </>
        )}
      </div>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>Upcoming Follow-Ups</CardTitle>
            <CardDescription>Your next follow-up tasks across all opportunities.</CardDescription>
          </div>
        </CardHeader>
        <CardContent className="px-0 pb-0">
          {upcomingLoading ? (
            <div className="px-5 pb-5">
              <Skeleton className="h-40 w-full" />
            </div>
          ) : upcomingIsError ? (
            <ErrorState title="Couldn't load follow-ups" error={upcomingError} onRetry={() => refetchUpcoming()} />
          ) : !upcoming?.length ? (
            <EmptyState title="Nothing upcoming" description="You're all caught up on follow-ups." />
          ) : (
            <ul className="divide-y divide-border">
              {upcoming.map((followup) => (
                <li key={followup.id} className="flex items-center justify-between px-5 py-3.5">
                  <div>
                    <p className="text-sm font-medium text-ink-900 line-clamp-1">{followup.note}</p>
                    <p className="text-xs text-ink-400">Due {formatDate(followup.next_followup_date)}</p>
                  </div>
                  <Link
                    to={`/opportunities/${followup.opportunity}`}
                    className="text-xs font-medium text-brand-600 hover:underline"
                  >
                    View
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
