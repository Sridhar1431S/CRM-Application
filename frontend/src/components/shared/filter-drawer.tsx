import * as React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { SlidersHorizontal, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface FilterDrawerProps {
  children: React.ReactNode;
  onClear?: () => void;
  activeCount?: number;
}

export function FilterDrawer({ children, onClear, activeCount = 0 }: FilterDrawerProps) {
  const [open, setOpen] = React.useState(false);

  return (
    <DialogPrimitive.Root open={open} onOpenChange={setOpen}>
      <DialogPrimitive.Trigger asChild>
        <Button variant="secondary" size="md" className="relative">
          <SlidersHorizontal className="h-4 w-4" />
          Filters
          {activeCount > 0 && (
            <span className="ml-1 flex h-5 w-5 items-center justify-center rounded-full bg-brand-600 text-[10px] font-semibold text-white">
              {activeCount}
            </span>
          )}
        </Button>
      </DialogPrimitive.Trigger>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-ink-900/30" />
        <DialogPrimitive.Content
          className={cn(
            "fixed right-0 top-0 z-50 h-full w-full max-w-xs border-l border-border bg-surface p-5 shadow-[var(--shadow-popover)]",
            "data-[state=open]:animate-in data-[state=open]:slide-in-from-right",
            "data-[state=closed]:animate-out data-[state=closed]:slide-out-to-right"
          )}
        >
          <div className="mb-5 flex items-center justify-between">
            <DialogPrimitive.Title className="text-sm font-semibold text-ink-900">
              Advanced filters
            </DialogPrimitive.Title>
            <DialogPrimitive.Close className="rounded-md p-1 text-ink-400 hover:bg-canvas hover:text-ink-700">
              <X className="h-4 w-4" />
            </DialogPrimitive.Close>
          </div>
          <div className="flex flex-col gap-4">{children}</div>
          {onClear && (
            <Button variant="ghost" size="sm" className="mt-6 w-full" onClick={onClear}>
              Clear all filters
            </Button>
          )}
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}
