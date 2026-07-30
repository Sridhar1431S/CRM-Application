import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Plus, TrendingUp } from "lucide-react";
import { opportunitiesApi } from "@/api/opportunities";
import { salesRepsApi } from "@/api/sales-reps";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Select } from "@/components/ui/input";
import { StageBadge } from "@/components/ui/badge";
import { DataTable, type DataTableColumn } from "@/components/shared/data-table";
import { Pagination } from "@/components/shared/pagination";
import { SearchBar } from "@/components/shared/search-bar";
import { FilterDrawer } from "@/components/shared/filter-drawer";
import { EmptyState } from "@/components/shared/empty-state";
import { useDebouncedValue } from "@/lib/use-debounced-value";
import { formatCurrency, formatDate } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";
import { OpportunityFormDialog } from "@/pages/opportunities/opportunity-form-dialog";
import type { Opportunity } from "@/types";

export default function OpportunitiesPage() {
  const isAdmin = useAuthStore((s) => s.user?.role === "admin");
  const navigate = useNavigate();

  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [stage, setStage] = useState("");
  const [assignedRep, setAssignedRep] = useState("");
  const [ordering, setOrdering] = useState("-created_at");
  const debouncedSearch = useDebouncedValue(search);
  const [formOpen, setFormOpen] = useState(false);

  const { data: repsForFilter } = useQuery({
    queryKey: ["sales-reps", "filter-list"],
    queryFn: () => salesRepsApi.list({ page_size: 100 }),
  });

  const { data, isLoading } = useQuery({
    queryKey: ["opportunities", { page, search: debouncedSearch, stage, assignedRep, ordering }],
    queryFn: () => opportunitiesApi.list({ page, search: debouncedSearch, stage, assigned_rep: assignedRep, ordering }),
    placeholderData: (prev) => prev,
  });

  const columns: DataTableColumn<Opportunity>[] = [
    {
      key: "customer",
      header: "Customer",
      render: (o) => <p className="font-medium text-ink-900">{o.customer_detail.company_name}</p>,
    },
    {
      key: "assigned_rep",
      header: "Sales Representative",
      render: (o) => o.assigned_rep_detail?.name ?? <span className="text-ink-400">Unassigned</span>,
    },
    {
      key: "estimated_value",
      header: "Value",
      sortable: true,
      render: (o) => formatCurrency(o.estimated_value),
    },
    {
      key: "expected_closing_date",
      header: "Expected Close",
      sortable: true,
      render: (o) => formatDate(o.expected_closing_date),
    },
    { key: "stage", header: "Stage", sortable: true, render: (o) => <StageBadge stage={o.stage} /> },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-ink-900">Opportunities</h2>
          <p className="text-sm text-ink-500">Track deals moving through your sales pipeline.</p>
        </div>
        {isAdmin && (
          <Button onClick={() => setFormOpen(true)}>
            <Plus className="h-4 w-4" />
            New opportunity
          </Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchBar value={search} onChange={setSearch} placeholder="Search by customer" className="max-w-sm flex-1" />
        <FilterDrawer
          activeCount={(stage ? 1 : 0) + (assignedRep ? 1 : 0)}
          onClear={() => {
            setStage("");
            setAssignedRep("");
          }}
        >
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-700">Stage</label>
            <Select value={stage} onChange={(e) => setStage(e.target.value)}>
              <option value="">All stages</option>
              <option value="qualification">Qualification</option>
              <option value="proposal">Proposal</option>
              <option value="negotiation">Negotiation</option>
              <option value="won">Won</option>
              <option value="lost">Lost</option>
            </Select>
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-700">Sales Representative</label>
            <Select value={assignedRep} onChange={(e) => setAssignedRep(e.target.value)}>
              <option value="">All representatives</option>
              {repsForFilter?.results.map((rep) => (
                <option key={rep.id} value={rep.id}>
                  {rep.name}
                </option>
              ))}
            </Select>
          </div>
        </FilterDrawer>
      </div>

      <Card>
        {!isLoading && data?.results.length === 0 ? (
          <EmptyState icon={TrendingUp} title="No opportunities found" description="Convert a lead to create your first opportunity." />
        ) : (
          <>
            <DataTable
              columns={columns}
              data={data?.results ?? []}
              rowKey={(o) => o.id}
              isLoading={isLoading}
              ordering={ordering}
              onOrderingChange={(o) => {
                setOrdering(o);
                setPage(1);
              }}
              onRowClick={(o) => navigate(`/opportunities/${o.id}`)}
            />
            {data && (
              <Pagination
                currentPage={data.current_page}
                totalPages={data.total_pages}
                count={data.count}
                onPageChange={setPage}
              />
            )}
          </>
        )}
      </Card>

      <OpportunityFormDialog open={formOpen} onOpenChange={setFormOpen} />
    </div>
  );
}
