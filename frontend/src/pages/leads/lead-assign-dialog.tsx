import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { salesRepsApi } from "@/api/sales-reps";
import { leadsApi } from "@/api/leads";
import { Button } from "@/components/ui/button";
import { Label, Select } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api-client";
import type { Lead } from "@/types";

export function LeadAssignDialog({
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
  const [repId, setRepId] = useState("");

  const { data: reps } = useQuery({
    queryKey: ["sales-reps", "all-active"],
    queryFn: () => salesRepsApi.list({ page_size: 100, is_active: true }),
    enabled: open,
  });

  const mutation = useMutation({
    mutationFn: () => leadsApi.assign(lead!.id, repId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      toast({ title: "Lead assigned", variant: "success" });
      onOpenChange(false);
      setRepId("");
    },
    onError: (error) => {
      toast({ title: "Couldn't assign lead", description: extractErrorMessage(error), variant: "error" });
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>Assign lead</DialogTitle>
          <DialogDescription>Choose a sales representative for "{lead?.company_name}".</DialogDescription>
        </DialogHeader>
        <div>
          <Label htmlFor="rep">Sales representative</Label>
          <Select id="rep" value={repId} onChange={(e) => setRepId(e.target.value)}>
            <option value="">Select a representative</option>
            {reps?.results.map((rep) => (
              <option key={rep.id} value={rep.id}>
                {rep.name}
              </option>
            ))}
          </Select>
        </div>
        <DialogFooter>
          <Button variant="secondary" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button disabled={!repId || mutation.isPending} onClick={() => mutation.mutate()}>
            {mutation.isPending ? "Assigning..." : "Assign"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
