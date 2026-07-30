import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, UserPlus, ArrowRightCircle, Target } from "lucide-react";
import { leadsApi } from "@/api/leads";
import { salesRepsApi } from "@/api/sales-reps";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Select } from "@/components/ui/input";
import { LeadStatusBadge, PriorityBadge } from "@/components/ui/badge";
import { DataTable, type DataTableColumn } from "@/components/shared/data-table";
import { Pagination } from "@/components/shared/pagination";
import { SearchBar } from "@/components/shared/search-bar";
import { FilterDrawer } from "@/components/shared/filter-drawer";
import { ConfirmModal } from "@/components/shared/confirm-modal";
import { EmptyState } from "@/components/shared/empty-state";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api-client";
import { useDebouncedValue } from "@/lib/use-debounced-value";
import { useAuthStore } from "@/store/auth-store";
import { LeadFormDialog } from "@/pages/leads/lead-form-dialog";
import { LeadAssignDialog } from "@/pages/leads/lead-assign-dialog";
import { LeadConvertDialog } from "@/pages/leads/lead-convert-dialog";
import type { Lead } from "@/types";

export default function LeadsPage() {
  const isAdmin = useAuthStore((s) => s.user?.role === "admin");
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [priority, setPriority] = useState("");
  const [assignedRep, setAssignedRep] = useState("");
  const [ordering, setOrdering] = useState("-created_at");
  const debouncedSearch = useDebouncedValue(search);

  const [formOpen, setFormOpen] = useState(false);
  const [editingLead, setEditingLead] = useState<Lead | null>(null);
  const [deletingLead, setDeletingLead] = useState<Lead | null>(null);
  const [assigningLead, setAssigningLead] = useState<Lead | null>(null);
  const [convertingLead, setConvertingLead] = useState<Lead | null>(null);

  const { data: repsForFilter } = useQuery({
    queryKey: ["sales-reps", "filter-list"],
    queryFn: () => salesRepsApi.list({ page_size: 100 }),
  });

  const { data, isLoading } = useQuery({
    queryKey: ["leads", { page, search: debouncedSearch, status, priority, assignedRep, ordering }],
    queryFn: () => leadsApi.list({ page, search: debouncedSearch, status, priority, assigned_rep: assignedRep, ordering }),
    placeholderData: (prev) => prev,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => leadsApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast({ title: "Lead deleted", variant: "success" });
      setDeletingLead(null);
    },
    onError: (error) => {
      toast({ title: "Couldn't delete lead", description: extractErrorMessage(error), variant: "error" });
    },
  });

  const columns: DataTableColumn<Lead>[] = [
    {
      key: "company_name",
      header: "Lead",
      sortable: true,
      render: (l) => (
        <div>
          <p className="font-medium text-ink-900">{l.company_name}</p>
          <p className="text-xs text-ink-400">{l.contact_name}</p>
        </div>
      ),
    },
    { key: "source", header: "Source", render: (l) => l.source || "—" },
    { key: "priority", header: "Priority", sortable: true, render: (l) => <PriorityBadge priority={l.priority} /> },
    { key: "status", header: "Status", sortable: true, render: (l) => <LeadStatusBadge status={l.status} /> },
    {
      key: "assigned_rep",
      header: "Assigned To",
      render: (l) => l.assigned_rep_detail?.name ?? <span className="text-ink-400">Unassigned</span>,
    },
  ];

  if (isAdmin) {
    columns.push({
      key: "actions",
      header: "",
      className: "text-right",
      render: (l) => (
        <div className="flex justify-end gap-1">
          <Button
            variant="ghost"
            size="icon"
            title="Assign"
            onClick={(e) => {
              e.stopPropagation();
              setAssigningLead(l);
            }}
          >
            <UserPlus className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            title="Convert to opportunity"
            disabled={l.converted_to_opportunity}
            onClick={(e) => {
              e.stopPropagation();
              setConvertingLead(l);
            }}
          >
            <ArrowRightCircle className={`h-4 w-4 ${l.converted_to_opportunity ? "text-ink-300" : "text-success-600"}`} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            title="Edit"
            onClick={(e) => {
              e.stopPropagation();
              setEditingLead(l);
              setFormOpen(true);
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            title="Delete"
            onClick={(e) => {
              e.stopPropagation();
              setDeletingLead(l);
            }}
          >
            <Trash2 className="h-4 w-4 text-danger-600" />
          </Button>
        </div>
      ),
    });
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-ink-900">Leads</h2>
          <p className="text-sm text-ink-500">Track and qualify incoming sales leads.</p>
        </div>
        {isAdmin && (
          <Button
            onClick={() => {
              setEditingLead(null);
              setFormOpen(true);
            }}
          >
            <Plus className="h-4 w-4" />
            New lead
          </Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchBar value={search} onChange={setSearch} placeholder="Search by company, contact, or email" className="max-w-sm flex-1" />
        <FilterDrawer
          activeCount={(status ? 1 : 0) + (priority ? 1 : 0) + (assignedRep ? 1 : 0)}
          onClear={() => {
            setStatus("");
            setPriority("");
            setAssignedRep("");
          }}
        >
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-700">Status</label>
            <Select value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">All statuses</option>
              <option value="new">New</option>
              <option value="contacted">Contacted</option>
              <option value="qualified">Qualified</option>
              <option value="lost">Lost</option>
            </Select>
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-700">Priority</label>
            <Select value={priority} onChange={(e) => setPriority(e.target.value)}>
              <option value="">All priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
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
          <EmptyState icon={Target} title="No leads found" description="Try adjusting your search or filters." />
        ) : (
          <>
            <DataTable
              columns={columns}
              data={data?.results ?? []}
              rowKey={(l) => l.id}
              isLoading={isLoading}
              ordering={ordering}
              onOrderingChange={(o) => {
                setOrdering(o);
                setPage(1);
              }}
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

      <LeadFormDialog open={formOpen} onOpenChange={setFormOpen} lead={editingLead} />
      <LeadAssignDialog open={!!assigningLead} onOpenChange={(o) => !o && setAssigningLead(null)} lead={assigningLead} />
      <LeadConvertDialog open={!!convertingLead} onOpenChange={(o) => !o && setConvertingLead(null)} lead={convertingLead} />

      <ConfirmModal
        open={!!deletingLead}
        onOpenChange={(open) => !open && setDeletingLead(null)}
        title="Delete lead?"
        description={`This will permanently remove "${deletingLead?.company_name}".`}
        confirmLabel="Delete"
        isLoading={deleteMutation.isPending}
        onConfirm={() => deletingLead && deleteMutation.mutate(deletingLead.id)}
      />
    </div>
  );
}
