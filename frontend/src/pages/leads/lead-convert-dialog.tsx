import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";
import { leadsApi } from "@/api/leads";
import { Button } from "@/components/ui/button";
import { Input, Label, FieldError } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { useEntityMutation } from "@/lib/use-entity-mutation";
import { estimatedValueField, expectedClosingDateField } from "@/lib/validation";
import type { Lead, Opportunity } from "@/types";

const schema = z.object({
  estimated_value: estimatedValueField,
  expected_closing_date: expectedClosingDateField,
});

type FormValues = z.infer<typeof schema>;

export function LeadConvertDialog({
  open,
  onOpenChange,
  lead,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  lead: Lead | null;
}) {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const mutation = useEntityMutation<Opportunity, FormValues>({
    mutationFn: (data) =>
      leadsApi.convert(lead!.id, {
        estimated_value: String(data.estimated_value),
        expected_closing_date: data.expected_closing_date,
      }),
    invalidateKeys: [["leads"], ["opportunities"], ["dashboard"]],
    successTitle: "Lead converted to opportunity",
    errorTitle: "Couldn't convert lead",
    onSuccess: (opportunity) => {
      onOpenChange(false);
      reset();
      navigate(`/opportunities/${opportunity.id}`);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>Convert to opportunity</DialogTitle>
          <DialogDescription>
            Turn "{lead?.company_name}" into a sales opportunity. The lead must already be assigned to a
            representative.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-4">
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
          <DialogFooter>
            <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Converting..." : "Convert"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
