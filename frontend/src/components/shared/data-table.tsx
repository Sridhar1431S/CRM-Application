import * as React from "react";
import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { TableSkeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";

export interface DataTableColumn<T> {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
  sortable?: boolean;
  className?: string;
}

interface DataTableProps<T> {
  columns: DataTableColumn<T>[];
  data: T[];
  rowKey: (row: T) => string;
  isLoading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  ordering?: string;
  onOrderingChange?: (ordering: string) => void;
  onRowClick?: (row: T) => void;
}

export function DataTable<T>({
  columns,
  data,
  rowKey,
  isLoading,
  emptyTitle = "No records found",
  emptyDescription = "Try adjusting your search or filters.",
  ordering,
  onOrderingChange,
  onRowClick,
}: DataTableProps<T>) {
  const handleSort = (key: string) => {
    if (!onOrderingChange) return;
    const isActive = ordering === key || ordering === `-${key}`;
    if (!isActive) {
      onOrderingChange(key);
    } else if (ordering === key) {
      onOrderingChange(`-${key}`);
    } else {
      onOrderingChange(key);
    }
  };

  if (isLoading) return <TableSkeleton cols={columns.length} />;
  if (data.length === 0) return <EmptyState title={emptyTitle} description={emptyDescription} />;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-[720px] w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-border bg-canvas/70">
            {columns.map((col) => {
              const isActive = ordering === col.key || ordering === `-${col.key}`;
              const isDesc = ordering === `-${col.key}`;
              return (
                <th
                  key={col.key}
                  className={cn(
                    "px-3 py-3 text-left text-xs font-semibold uppercase tracking-wide text-ink-500 sm:px-5",
                    col.sortable && "cursor-pointer select-none hover:text-ink-700",
                    col.className
                  )}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.header}
                    {col.sortable &&
                      (isActive ? (
                        isDesc ? (
                          <ArrowDown className="h-3 w-3" />
                        ) : (
                          <ArrowUp className="h-3 w-3" />
                        )
                      ) : (
                        <ArrowUpDown className="h-3 w-3 opacity-40" />
                      ))}
                  </span>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr
              key={rowKey(row)}
              className={cn(
                "border-b border-border last:border-0",
                onRowClick && "cursor-pointer hover:bg-canvas/60"
              )}
              onClick={() => onRowClick?.(row)}
            >
              {columns.map((col) => (
                <td key={col.key} className={cn("px-3 py-3.5 align-middle text-ink-700 sm:px-5", col.className)}>
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
