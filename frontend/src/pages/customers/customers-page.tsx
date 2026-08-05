import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Building2 } from "lucide-react";
import { customersApi } from "@/api/customers";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Select } from "@/components/ui/input";
import { StatusBadge } from "@/components/ui/badge";
import { DataTable, type DataTableColumn } from "@/components/shared/data-table";
import { Pagination } from "@/components/shared/pagination";
import { SearchBar } from "@/components/shared/search-bar";
import { FilterDrawer } from "@/components/shared/filter-drawer";
import { ConfirmModal } from "@/components/shared/confirm-modal";
import { EmptyState } from "@/components/shared/empty-state";
import { useEntityMutation } from "@/lib/use-entity-mutation";
import { useListControls } from "@/lib/use-list-controls";
import { useAuthStore } from "@/store/auth-store";
import { CustomerFormDialog } from "@/pages/customers/customer-form-dialog";
import type { Customer } from "@/types";

export default function CustomersPage() {
  const isAdmin = useAuthStore((s) => s.user?.role === "admin");

  const { page, setPage, search, setSearch, debouncedSearch, ordering, setOrdering } = useListControls();
  const [status, setStatus] = useState("");

  const [formOpen, setFormOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [deletingCustomer, setDeletingCustomer] = useState<Customer | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["customers", { page, search: debouncedSearch, status, ordering }],
    queryFn: () => customersApi.list({ page, search: debouncedSearch, status, ordering }),
    placeholderData: (prev) => prev,
  });

  const deleteMutation = useEntityMutation<unknown, string>({
    mutationFn: (id) => customersApi.remove(id),
    invalidateKeys: [["customers"], ["dashboard"]],
    successTitle: "Customer deleted",
    errorTitle: "Couldn't delete customer",
    onSuccess: () => setDeletingCustomer(null),
  });

  const columns: DataTableColumn<Customer>[] = [
    {
      key: "company_name",
      header: "Company",
      sortable: true,
      render: (c) => (
        <div>
          <p className="font-medium text-ink-900">{c.company_name}</p>
          <p className="text-xs text-ink-400">{c.industry || "—"}</p>
        </div>
      ),
    },
    { key: "contact_person", header: "Contact", render: (c) => c.contact_person },
    {
      key: "email",
      header: "Email / Phone",
      render: (c) => (
        <div>
          <p>{c.email}</p>
          <p className="text-xs text-ink-400">{c.phone_number}</p>
        </div>
      ),
    },
    { key: "status", header: "Status", sortable: true, render: (c) => <StatusBadge status={c.status} /> },
  ];

  if (isAdmin) {
    columns.push({
      key: "actions",
      header: "",
      className: "text-right",
      render: (c) => (
        <div className="flex justify-end gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => {
              e.stopPropagation();
              setEditingCustomer(c);
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
              setDeletingCustomer(c);
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
          <h2 className="text-lg font-semibold text-ink-900">Customers</h2>
          <p className="text-sm text-ink-500">Manage your customer accounts and relationships.</p>
        </div>
        {isAdmin && (
          <Button
            onClick={() => {
              setEditingCustomer(null);
              setFormOpen(true);
            }}
          >
            <Plus className="h-4 w-4" />
            New customer
          </Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchBar value={search} onChange={setSearch} placeholder="Search by company, contact, or email" className="max-w-sm flex-1" />
        <FilterDrawer activeCount={status ? 1 : 0} onClear={() => setStatus("")}>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-700">Status</label>
            <Select value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">All statuses</option>
              <option value="prospect">Prospect</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </Select>
          </div>
        </FilterDrawer>
      </div>

      <Card>
        {!isLoading && data?.results.length === 0 ? (
          <EmptyState
            icon={Building2}
            title="No customers found"
            description="Try adjusting your search or filters, or add a new customer."
          />
        ) : (
          <>
            <DataTable
              columns={columns}
              data={data?.results ?? []}
              rowKey={(c) => c.id}
              isLoading={isLoading}
              ordering={ordering}
              onOrderingChange={setOrdering}
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

      <CustomerFormDialog open={formOpen} onOpenChange={setFormOpen} customer={editingCustomer} />

      <ConfirmModal
        open={!!deletingCustomer}
        onOpenChange={(open) => !open && setDeletingCustomer(null)}
        title="Delete customer?"
        description={`This will remove "${deletingCustomer?.company_name}". Customers with open opportunities can't be deleted.`}
        confirmLabel="Delete"
        isLoading={deleteMutation.isPending}
        onConfirm={() => deletingCustomer && deleteMutation.mutate(deletingCustomer.id)}
      />
    </div>
  );
}
