import { useParams, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Building2, CalendarDays, IndianRupee, User as UserIcon } from "lucide-react";
import { opportunitiesApi } from "@/api/opportunities";
import { followupsApi } from "@/api/followups";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StageBadge } from "@/components/ui/badge";
import { Select, Textarea, Label, Input, FieldError } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api-client";
import { formatCurrency, formatDate, initials } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";
import type { OpportunityStage } from "@/types";

const followupSchema = z.object({
  note: z.string().min(1, "Note is required"),
  next_followup_date: z.string().optional(),
});
type FollowUpFormValues = z.infer<typeof followupSchema>;

const STAGES: OpportunityStage[] = ["qualification", "proposal", "negotiation", "won", "lost"];

export default function OpportunityDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const user = useAuthStore((s) => s.user);

  const { data: opportunity, isLoading } = useQuery({
    queryKey: ["opportunities", id],
    queryFn: () => opportunitiesApi.get(id!),
    enabled: !!id,
  });

  const { data: followups, isLoading: followupsLoading } = useQuery({
    queryKey: ["followups", id],
    queryFn: () => followupsApi.listForOpportunity(id!),
    enabled: !!id,
  });

  const canManage = user?.role === "admin" || opportunity?.assigned_rep === user?.id;
  const isTerminal = opportunity?.stage === "won" || opportunity?.stage === "lost";

  const stageMutation = useMutation({
    mutationFn: (stage: OpportunityStage) => opportunitiesApi.updateStage(id!, stage),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["opportunities"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast({ title: "Stage updated", variant: "success" });
    },
    onError: (error) => {
      toast({ title: "Couldn't update stage", description: extractErrorMessage(error), variant: "error" });
    },
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FollowUpFormValues>({ resolver: zodResolver(followupSchema) });

  const followupMutation = useMutation({
    mutationFn: (data: FollowUpFormValues) =>
      followupsApi.create(id!, { note: data.note, next_followup_date: data.next_followup_date || null }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["followups", id] });
      queryClient.invalidateQueries({ queryKey: ["followups", "upcoming"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast({ title: "Follow-up logged", variant: "success" });
      reset();
    },
    onError: (error) => {
      toast({ title: "Couldn't log follow-up", description: extractErrorMessage(error), variant: "error" });
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!opportunity) {
    return <EmptyState title="Opportunity not found" description="It may have been deleted or you don't have access." />;
  }

  return (
    <div className="space-y-4">
      <button
        onClick={() => navigate("/opportunities")}
        className="flex items-center gap-1.5 text-sm font-medium text-ink-500 hover:text-ink-900"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to opportunities
      </button>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-ink-900">{opportunity.customer_detail.company_name}</h2>
          <p className="text-sm text-ink-500">{opportunity.customer_detail.contact_person}</p>
        </div>
        <StageBadge stage={opportunity.stage} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="p-5">
          <div className="flex items-center gap-3">
            <IndianRupee className="h-4 w-4 text-ink-400" />
            <div>
              <p className="text-xs text-ink-500">Estimated value</p>
              <p className="text-sm font-semibold text-ink-900">{formatCurrency(opportunity.estimated_value)}</p>
            </div>
          </div>
        </Card>
        <Card className="p-5">
          <div className="flex items-center gap-3">
            <CalendarDays className="h-4 w-4 text-ink-400" />
            <div>
              <p className="text-xs text-ink-500">Expected closing date</p>
              <p className="text-sm font-semibold text-ink-900">{formatDate(opportunity.expected_closing_date)}</p>
            </div>
          </div>
        </Card>
        <Card className="p-5">
          <div className="flex items-center gap-3">
            <UserIcon className="h-4 w-4 text-ink-400" />
            <div>
              <p className="text-xs text-ink-500">Assigned representative</p>
              <p className="text-sm font-semibold text-ink-900">{opportunity.assigned_rep_detail?.name ?? "Unassigned"}</p>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Update stage</CardTitle>
        </CardHeader>
        <CardContent>
          {!canManage ? (
            <p className="text-sm text-ink-500">Only the assigned sales representative or an administrator can update this opportunity.</p>
          ) : isTerminal ? (
            <p className="text-sm text-ink-500">
              This opportunity is <span className="font-medium">{opportunity.stage}</span> and is closed. Closed
              opportunities cannot be moved to another stage.
            </p>
          ) : (
            <div className="flex items-center gap-3">
              <Select
                value={opportunity.stage}
                onChange={(e) => stageMutation.mutate(e.target.value as OpportunityStage)}
                disabled={stageMutation.isPending}
                className="max-w-xs"
              >
                {STAGES.map((s) => (
                  <option key={s} value={s}>
                    {s.charAt(0).toUpperCase() + s.slice(1)}
                  </option>
                ))}
              </Select>
              {stageMutation.isPending && <span className="text-xs text-ink-400">Updating...</span>}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Building2 className="h-4 w-4 text-ink-400" />
            <CardTitle>Follow-Up History</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {canManage && (
            <form
              onSubmit={handleSubmit((data) => followupMutation.mutate(data))}
              className="mb-5 space-y-3 rounded-lg border border-border bg-canvas/40 p-4"
            >
              <div>
                <Label htmlFor="note">Follow-up note</Label>
                <Textarea id="note" rows={3} placeholder="What happened in this interaction?" {...register("note")} />
                <FieldError message={errors.note?.message} />
              </div>
              <div className="flex items-end gap-3">
                <div className="flex-1">
                  <Label htmlFor="next_followup_date">Next follow-up date (optional)</Label>
                  <Input id="next_followup_date" type="date" {...register("next_followup_date")} />
                </div>
                <Button type="submit" disabled={followupMutation.isPending}>
                  {followupMutation.isPending ? "Logging..." : "Log follow-up"}
                </Button>
              </div>
            </form>
          )}

          {followupsLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : !followups?.results.length ? (
            <EmptyState title="No follow-ups yet" description="Log the first interaction with this opportunity." />
          ) : (
            <ul className="space-y-3">
              {followups.results.map((f) => (
                <li key={f.id} className="flex gap-3 rounded-lg border border-border p-3.5">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                    {f.created_by_detail ? initials(f.created_by_detail.name) : "?"}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-ink-900">{f.created_by_detail?.name ?? "Unknown"}</p>
                      <p className="text-xs text-ink-400">{formatDate(f.created_at)}</p>
                    </div>
                    <p className="mt-1 text-sm text-ink-700">{f.note}</p>
                    {f.next_followup_date && (
                      <p className="mt-1 text-xs text-brand-600">Next follow-up: {formatDate(f.next_followup_date)}</p>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
