import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { Users, Target, TrendingUp, UserCog } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { dashboardApi } from "@/api/dashboard";
import { KpiCard } from "@/components/shared/kpi-card";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { formatCurrency, formatDate } from "@/lib/utils";
import { DataTable } from "@/components/shared/data-table";
import { StageBadge } from "@/components/ui/badge";
import type { OpportunityStage, ProgressMonitoringRow } from "@/types";

const stageLabels: Record<OpportunityStage, string> = {
  qualification: "Qualification",
  proposal: "Proposal",
  negotiation: "Negotiation",
  won: "Won",
  lost: "Lost",
};

const stageOrder: OpportunityStage[] = ["qualification", "proposal", "negotiation", "won", "lost"];

export default function AdminDashboardPage() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["dashboard", "admin"],
    queryFn: dashboardApi.admin,
  });
  const [ordering, setOrdering] = React.useState("-value");

  const rows = React.useMemo(() => data?.progress_monitoring ?? [], [data]);

  const sortedRows = React.useMemo(() => {
    const sortKey = ordering.startsWith("-") ? ordering.slice(1) : ordering;
    const direction = ordering.startsWith("-") ? -1 : 1;

    return [...rows].sort((left, right) => {
      if (sortKey === "value") {
        const leftNum = Number(left.value || 0);
        const rightNum = Number(right.value || 0);
        return (leftNum - rightNum) * direction;
      }

      if (sortKey === "expected_close") {
        const leftTime = new Date(left.expected_close).getTime();
        const rightTime = new Date(right.expected_close).getTime();
        return (leftTime - rightTime) * direction;
      }

      return String(left[sortKey as keyof ProgressMonitoringRow] ?? "").localeCompare(
        String(right[sortKey as keyof ProgressMonitoringRow] ?? "")
      ) * direction;
    });
  }, [ordering, rows]);

  const chartData = React.useMemo(() => {
    return stageOrder.map((stage) => {
      const stageRows = rows.filter((row) => row.stage === stage);
      const totalValue = stageRows.reduce((sum, row) => sum + Number(row.value || 0), 0);
      return {
        stage,
        label: stageLabels[stage],
        count: stageRows.length,
        value: totalValue,
      };
    });
  }, [rows]);

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold text-ink-900">Administrator Dashboard</h2>
        <p className="text-sm text-ink-500">A live snapshot of your team's pipeline.</p>
      </div>

      {isError && (
        <Card>
          <ErrorState title="Couldn't load the dashboard" error={error} onRetry={() => refetch()} />
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-[92px] rounded-[var(--radius-card)]" />)
        ) : (
          <>
            <KpiCard label="Total Customers" value={data?.summary.total_customers ?? 0} icon={Users} tone="brand" />
            <KpiCard label="Total Leads" value={data?.summary.total_leads ?? 0} icon={Target} tone="info" />
            <KpiCard label="Open Opportunities" value={data?.summary.open_opportunities ?? 0} icon={TrendingUp} tone="warning" />
            <KpiCard label="Active Sales Representatives" value={data?.summary.active_sales_representatives ?? 0} icon={UserCog} tone="success" />
          </>
        )}
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Pipeline by stage</CardTitle>
              <CardDescription>Opportunity volume across each stage of the funnel.</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                    <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fill: "var(--color-ink-500)", fontSize: 12 }} />
                    <YAxis tickLine={false} axisLine={false} tick={{ fill: "var(--color-ink-500)", fontSize: 12 }} />
                    <Tooltip
                      cursor={{ fill: "rgba(51, 88, 244, 0.08)" }}
                      contentStyle={{
                        backgroundColor: "var(--color-surface)",
                        border: "1px solid var(--color-border)",
                        borderRadius: "0.75rem",
                        color: "var(--color-ink-900)",
                      }}
                    />
                    <Bar dataKey="count" radius={[6, 6, 0, 0]} fill="#3358F4" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Value by stage</CardTitle>
              <CardDescription>Revenue potential flowing through each stage.</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                    <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fill: "var(--color-ink-500)", fontSize: 12 }} />
                    <YAxis tickLine={false} axisLine={false} tick={{ fill: "var(--color-ink-500)", fontSize: 12 }} />
                    <Tooltip
                      formatter={(value) => formatCurrency(Number(value ?? 0))}
                      contentStyle={{
                        backgroundColor: "var(--color-surface)",
                        border: "1px solid var(--color-border)",
                        borderRadius: "0.75rem",
                        color: "var(--color-ink-900)",
                      }}
                    />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]} fill="#7a86fb" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>Progress Monitoring</CardTitle>
            <CardDescription>Live view of every opportunity across the team.</CardDescription>
          </div>
        </CardHeader>
        <CardContent className="px-0 pb-0">
          {isLoading ? (
            <div className="px-5 pb-5">
              <Skeleton className="h-64 w-full" />
            </div>
          ) : isError ? (
            <ErrorState title="Couldn't load progress monitoring" error={error} onRetry={() => refetch()} />
          ) : !rows.length ? (
            <EmptyState title="No opportunities yet" description="Convert a lead to see it appear here." />
          ) : (
            <DataTable
              columns={[
                { key: "customer", header: "Customer", sortable: true, render: (row) => <span className="font-medium text-ink-900">{row.customer}</span> },
                { key: "sales_representative", header: "Sales Representative", sortable: true, render: (row) => <span className="text-ink-700">{row.sales_representative ?? "Unassigned"}</span> },
                { key: "stage", header: "Stage", sortable: true, render: (row) => <StageBadge stage={row.stage} /> },
                { key: "value", header: "Value", sortable: true, render: (row) => <span className="text-ink-700">{formatCurrency(row.value)}</span> },
                { key: "expected_close", header: "Expected Close", sortable: true, render: (row) => <span className="text-ink-700">{formatDate(row.expected_close)}</span> },
              ]}
              data={sortedRows}
              rowKey={(row) => row.opportunity_id}
              ordering={ordering}
              onOrderingChange={setOrdering}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
