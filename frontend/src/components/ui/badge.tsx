import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium", {
  variants: {
    tone: {
      neutral: "bg-canvas text-ink-700 border border-border",
      brand: "bg-brand-50 text-brand-700",
      success: "bg-success-50 text-success-700",
      warning: "bg-warning-50 text-warning-700",
      danger: "bg-danger-50 text-danger-700",
      info: "bg-info-50 text-info-700",
    },
  },
  defaultVariants: { tone: "neutral" },
});

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {
  dot?: boolean;
}

export function Badge({ className, tone, dot, children, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ tone, className }))} {...props}>
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {children}
    </span>
  );
}

const CUSTOMER_STATUS_TONE: Record<string, BadgeProps["tone"]> = {
  prospect: "info",
  active: "success",
  inactive: "neutral",
};

const LEAD_STATUS_TONE: Record<string, BadgeProps["tone"]> = {
  new: "info",
  contacted: "brand",
  qualified: "success",
  lost: "danger",
};

const PRIORITY_TONE: Record<string, BadgeProps["tone"]> = {
  low: "neutral",
  medium: "warning",
  high: "danger",
};

const STAGE_TONE: Record<string, BadgeProps["tone"]> = {
  qualification: "info",
  proposal: "brand",
  negotiation: "warning",
  won: "success",
  lost: "danger",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <Badge tone={CUSTOMER_STATUS_TONE[status] ?? "neutral"} dot>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
}

export function LeadStatusBadge({ status }: { status: string }) {
  return (
    <Badge tone={LEAD_STATUS_TONE[status] ?? "neutral"} dot>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
}

export function PriorityBadge({ priority }: { priority: string }) {
  return (
    <Badge tone={PRIORITY_TONE[priority] ?? "neutral"}>{priority.charAt(0).toUpperCase() + priority.slice(1)}</Badge>
  );
}

export function StageBadge({ stage }: { stage: string }) {
  const label = stage.charAt(0).toUpperCase() + stage.slice(1);
  return (
    <Badge tone={STAGE_TONE[stage] ?? "neutral"} dot>
      {label}
    </Badge>
  );
}
