import { useEffect } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { opportunitiesApi } from "@/api/opportunities";
import { customersApi } from "@/api/customers";
import { salesRepsApi } from "@/api/sales-reps";
import { Button } from "@/components/ui/button";
import { Input, Label, FieldError, Select } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api-client";
import type { Opportunity } from "@/types";

const schema = z.object({
  customer: z.string().min(1, "Customer is required"),
  assigned_rep: z.string().min(1, "Assigned representative is required"),
  estimated_value: z.coerce.number().positive("Value must be greater than zero"),
  expected_closing_date: z.string().min(1, "Expected closing date is required"),
  stage: z.enum(["qualification", "proposal", "negotiation", "won", "lost"]),
});

type FormValues = z.infer<typeof schema>;

interface OpportunityFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  opportunity?: Opportunity | null;
}

export function OpportunityFormDialog({ open, onOpenChange, opportunity }: OpportunityFormDialogProps) {
  const isEdit = !!opportunity;
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: customers } = useQuery({
    queryKey: ["customers", "all-picker"],
    queryFn: () => customersApi.list({ page_size: 100 }),
    enabled: open,
  });
  const { data: reps } = useQuery({
    queryKey: ["sales-reps", "all-active"],
    queryFn: () => salesRepsApi.list({ page_size: 100, is_active: true }),
    enabled: open,
  });

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  useEffect(() => {
    if (open) {
      reset(
        opportunity
          ? {
              customer: opportunity.customer,
              assigned_rep: opportunity.assigned_rep ?? "",
              estimated_value: Number(opportunity.estimated_value),
              expected_closing_date: opportunity.expected_closing_date,
              stage: opportunity.stage,
            }
          : {
              customer: "",
              assigned_rep: "",
              estimated_value: undefined,
              expected_closing_date: "",
              stage: "qualification",
            }
      );
    }
  }, [open, opportunity, reset]);

  const mutation = useMutation({
    mutationFn: (data: FormValues) => {
      const payload = { ...data, estimated_value: String(data.estimated_value) };
      return isEdit ? opportunitiesApi.update(opportunity!.id, payload) : opportunitiesApi.create(payload as never);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["opportunities"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast({ title: isEdit ? "Opportunity updated" : "Opportunity created", variant: "success" });
      onOpenChange(false);
    },
    onError: (error) => {
      toast({ title: "Couldn't save opportunity", description: extractErrorMessage(error), variant: "error" });
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit opportunity" : "New opportunity"}</DialogTitle>
          <DialogDescription>
            {isEdit ? "Update this opportunity's details." : "Create a new sales opportunity."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-4">
          <div>
            <Label htmlFor="customer">Customer</Label>
            <Controller
              control={control}
              name="customer"
              render={({ field }) => (
                <Select id="customer" {...field}>
                  <option value="">Select a customer</option>
                  {customers?.results.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.company_name}
                    </option>
                  ))}
                </Select>
              )}
            />
            <FieldError message={errors.customer?.message} />
          </div>
          <div>
            <Label htmlFor="assigned_rep">Assigned representative</Label>
            <Controller
              control={control}
              name="assigned_rep"
              render={({ field }) => (
                <Select id="assigned_rep" {...field}>
                  <option value="">Select a representative</option>
                  {reps?.results.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name}
                    </option>
                  ))}
                </Select>
              )}
            />
            <FieldError message={errors.assigned_rep?.message} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="estimated_value">Estimated value (₹)</Label>
              <Input id="estimated_value" type="number" step="0.01" min="0.01" {...register("estimated_value")} />
              <FieldError message={errors.estimated_value?.message} />
            </div>
            <div>
              <Label htmlFor="expected_closing_date">Expected closing date</Label>
              <Input id="expected_closing_date" type="date" {...register("expected_closing_date")} />
              <FieldError message={errors.expected_closing_date?.message} />
            </div>
          </div>
          <div>
            <Label htmlFor="stage">Stage</Label>
            <Controller
              control={control}
              name="stage"
              render={({ field }) => (
                <Select id="stage" {...field}>
                  <option value="qualification">Qualification</option>
                  <option value="proposal">Proposal</option>
                  <option value="negotiation">Negotiation</option>
                  <option value="won">Won</option>
                  <option value="lost">Lost</option>
                </Select>
              )}
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving..." : isEdit ? "Save changes" : "Create opportunity"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
