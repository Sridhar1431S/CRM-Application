import { useEffect } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { leadsApi } from "@/api/leads";
import { Button } from "@/components/ui/button";
import { Input, Label, FieldError, Select } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { useEntityFormMutation } from "@/lib/use-entity-mutation";
import { emailField, phoneNumberField, requiredField } from "@/lib/validation";
import type { Lead } from "@/types";

const schema = z.object({
  company_name: requiredField("Company name"),
  contact_name: requiredField("Contact name"),
  email: emailField,
  phone_number: phoneNumberField,
  source: z.string().optional(),
  priority: z.enum(["low", "medium", "high"]),
  status: z.enum(["new", "contacted", "qualified", "lost"]),
});

type FormValues = z.infer<typeof schema>;

interface LeadFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  lead?: Lead | null;
}

export function LeadFormDialog({ open, onOpenChange, lead }: LeadFormDialogProps) {
  const isEdit = !!lead;

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { priority: "medium", status: "new" } });

  useEffect(() => {
    if (open) {
      reset(
        lead
          ? {
              company_name: lead.company_name,
              contact_name: lead.contact_name,
              email: lead.email,
              phone_number: lead.phone_number,
              source: lead.source ?? "",
              priority: lead.priority,
              status: lead.status,
            }
          : {
              company_name: "",
              contact_name: "",
              email: "",
              phone_number: "",
              source: "",
              priority: "medium",
              status: "new",
            }
      );
    }
  }, [open, lead, reset]);

  const mutation = useEntityFormMutation<FormValues, Lead>({
    isEdit,
    entityLabel: "lead",
    resourceKey: "leads",
    save: (data) => (isEdit ? leadsApi.update(lead!.id, data) : leadsApi.create(data as Lead)),
    onSaved: () => onOpenChange(false),
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit lead" : "New lead"}</DialogTitle>
          <DialogDescription>{isEdit ? "Update this lead's details." : "Capture a new sales lead."}</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="company_name">Company name</Label>
              <Input id="company_name" {...register("company_name")} />
              <FieldError message={errors.company_name?.message} />
            </div>
            <div>
              <Label htmlFor="contact_name">Contact name</Label>
              <Input id="contact_name" {...register("contact_name")} />
              <FieldError message={errors.contact_name?.message} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" {...register("email")} />
              <FieldError message={errors.email?.message} />
            </div>
            <div>
              <Label htmlFor="phone_number">Phone number</Label>
              <Input id="phone_number" {...register("phone_number")} />
              <FieldError message={errors.phone_number?.message} />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label htmlFor="source">Source</Label>
              <Input id="source" placeholder="e.g. Referral" {...register("source")} />
            </div>
            <div>
              <Label htmlFor="priority">Priority</Label>
              <Controller
                control={control}
                name="priority"
                render={({ field }) => (
                  <Select id="priority" {...field}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </Select>
                )}
              />
            </div>
            <div>
              <Label htmlFor="status">Status</Label>
              <Controller
                control={control}
                name="status"
                render={({ field }) => (
                  <Select id="status" {...field}>
                    <option value="new">New</option>
                    <option value="contacted">Contacted</option>
                    <option value="qualified">Qualified</option>
                    <option value="lost">Lost</option>
                  </Select>
                )}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving..." : isEdit ? "Save changes" : "Create lead"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
