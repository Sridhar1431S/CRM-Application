import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Plus, Pencil, UserX, UserCheck, UserCog } from "lucide-react";
import { salesRepsApi } from "@/api/sales-reps";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable, type DataTableColumn } from "@/components/shared/data-table";
import { Pagination } from "@/components/shared/pagination";
import { SearchBar } from "@/components/shared/search-bar";
import { ConfirmModal } from "@/components/shared/confirm-modal";
import { EmptyState } from "@/components/shared/empty-state";
import { useEntityMutation } from "@/lib/use-entity-mutation";
import { useListControls } from "@/lib/use-list-controls";
import { initials, formatDate } from "@/lib/utils";
import { SalesRepFormDialog } from "@/pages/sales-reps/sales-rep-form-dialog";
import type { User } from "@/types";

export default function SalesRepsPage() {
  const { page, setPage, search, setSearch, debouncedSearch } = useListControls();

  const [formOpen, setFormOpen] = useState(false);
  const [editingRep, setEditingRep] = useState<User | null>(null);
  const [toggleTarget, setToggleTarget] = useState<User | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["sales-reps", { page, search: debouncedSearch }],
    queryFn: () => salesRepsApi.list({ page, search: debouncedSearch }),
    placeholderData: (prev) => prev,
  });

  const toggleMutation = useEntityMutation<User, User>({
    mutationFn: (rep) => (rep.is_active ? salesRepsApi.disable(rep.id) : salesRepsApi.enable(rep.id)),
    invalidateKeys: [["sales-reps"], ["dashboard"]],
    successTitle: (rep) => (rep.is_active ? "Representative disabled" : "Representative enabled"),
    errorTitle: "Couldn't update representative",
    onSuccess: () => setToggleTarget(null),
  });

  const columns: DataTableColumn<User>[] = [
    {
      key: "name",
      header: "Representative",
      sortable: true,
      render: (rep) => (
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
            {initials(rep.name)}
          </div>
          <div>
            <p className="font-medium text-ink-900">{rep.name}</p>
            <p className="text-xs text-ink-400">{rep.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: "is_active",
      header: "Status",
      render: (rep) => (
        <Badge tone={rep.is_active ? "success" : "neutral"} dot>
          {rep.is_active ? "Active" : "Disabled"}
        </Badge>
      ),
    },
    { key: "created_at", header: "Joined", sortable: true, render: (rep) => formatDate(rep.created_at) },
    {
      key: "actions",
      header: "",
      className: "text-right",
      render: (rep) => (
        <div className="flex justify-end gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => {
              e.stopPropagation();
              setEditingRep(rep);
              setFormOpen(true);
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => {
              e.stopPropagation();
              setToggleTarget(rep);
            }}
          >
            {rep.is_active ? (
              <UserX className="h-4 w-4 text-danger-600" />
            ) : (
              <UserCheck className="h-4 w-4 text-success-600" />
            )}
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-ink-900">Sales Representatives</h2>
          <p className="text-sm text-ink-500">Manage your team of sales representatives.</p>
        </div>
        <Button
          onClick={() => {
            setEditingRep(null);
            setFormOpen(true);
          }}
        >
          <Plus className="h-4 w-4" />
          New representative
        </Button>
      </div>

      <SearchBar value={search} onChange={setSearch} placeholder="Search by name or email" className="max-w-sm" />

      <Card>
        {!isLoading && data?.results.length === 0 ? (
          <EmptyState icon={UserCog} title="No sales representatives found" description="Add your first team member to get started." />
        ) : (
          <>
            <DataTable columns={columns} data={data?.results ?? []} rowKey={(r) => r.id} isLoading={isLoading} />
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

      <SalesRepFormDialog open={formOpen} onOpenChange={setFormOpen} rep={editingRep} />

      <ConfirmModal
        open={!!toggleTarget}
        onOpenChange={(open) => !open && setToggleTarget(null)}
        title={toggleTarget?.is_active ? "Disable representative?" : "Enable representative?"}
        description={
          toggleTarget?.is_active
            ? `${toggleTarget?.name} will no longer be able to log in or be assigned new leads.`
            : `${toggleTarget?.name} will regain access to the CRM.`
        }
        confirmLabel={toggleTarget?.is_active ? "Disable" : "Enable"}
        variant={toggleTarget?.is_active ? "danger" : "primary"}
        isLoading={toggleMutation.isPending}
        onConfirm={() => toggleTarget && toggleMutation.mutate(toggleTarget)}
      />
    </div>
  );
}
