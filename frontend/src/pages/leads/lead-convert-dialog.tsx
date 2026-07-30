import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { leadsApi } from "@/api/leads";
import { Button } from "@/components/ui/button";
import { Input, Label, FieldError } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api-client";
import type { Lead } from "@/types";

const schema = z.object({
  estimated_value: z.coerce.number().positive("Value must be greater than zero"),
  expected_closing_date: z.string().min(1, "Expected closing date is required"),
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
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const mutation = useMutation({
    mutationFn: (data: FormValues) =>
      leadsApi.convert(lead!.id, {
        estimated_value: String(data.estimated_value),
        expected_closing_date: data.expected_closing_date,
      }),
    onSuccess: (opportunity) => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      queryClient.invalidateQueries({ queryKey: ["opportunities"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast({ title: "Lead converted to opportunity", variant: "success" });
      onOpenChange(false);
      reset();
      navigate(`/opportunities/${opportunity.id}`);
    },
    onError: (error) => {
      toast({ title: "Couldn't convert lead", description: extractErrorMessage(error), variant: "error" });
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
