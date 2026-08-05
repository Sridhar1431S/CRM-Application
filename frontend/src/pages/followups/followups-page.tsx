import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { CalendarClock, ArrowRight } from "lucide-react";
import { followupsApi } from "@/api/followups";
import { Card } from "@/components/ui/card";
import { TableSkeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { formatDate, initials } from "@/lib/utils";

export default function FollowUpsPage() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["followups", "upcoming"],
    queryFn: followupsApi.upcoming,
  });

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-ink-900">Follow-Ups</h2>
        <p className="text-sm text-ink-500">Upcoming follow-up tasks across your opportunities.</p>
      </div>

      <Card>
        {isLoading ? (
          <TableSkeleton cols={4} />
        ) : isError ? (
          <ErrorState title="Couldn't load follow-ups" error={error} onRetry={() => refetch()} />
        ) : !data?.length ? (
          <EmptyState
            icon={CalendarClock}
            title="No upcoming follow-ups"
            description="Log a follow-up with a next date from any opportunity's detail page."
          />
        ) : (
          <ul className="divide-y divide-border">
            {data.map((followup) => (
              <li key={followup.id} className="flex items-center justify-between gap-4 px-5 py-4">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                    {followup.created_by_detail ? initials(followup.created_by_detail.name) : "?"}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-ink-900">{followup.note}</p>
                    <p className="mt-0.5 text-xs text-ink-400">
                      Due {formatDate(followup.next_followup_date)} · Logged by{" "}
                      {followup.created_by_detail?.name ?? "Unknown"}
                    </p>
                  </div>
                </div>
                <Button variant="secondary" size="sm" asChild>
                  <Link to={`/opportunities/${followup.opportunity}`}>
                    View opportunity
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </Button>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
