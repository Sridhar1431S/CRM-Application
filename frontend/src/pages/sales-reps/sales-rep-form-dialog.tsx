import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { salesRepsApi } from "@/api/sales-reps";
import { Button } from "@/components/ui/button";
import { Input, Label, FieldError } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { useEntityFormMutation } from "@/lib/use-entity-mutation";
import { emailField, requiredField } from "@/lib/validation";
import type { User } from "@/types";

const editSchema = z.object({
  name: requiredField("Name"),
  email: emailField,
});

const createSchema = editSchema.extend({
  password: z.string().min(8, "Password must be at least 8 characters"),
});

interface SalesRepFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  rep?: User | null;
}

export function SalesRepFormDialog({ open, onOpenChange, rep }: SalesRepFormDialogProps) {
  const isEdit = !!rep;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<{ name: string; email: string; password?: string }>({
    resolver: zodResolver(isEdit ? editSchema : createSchema),
  });

  useEffect(() => {
    if (open) {
      reset(rep ? { name: rep.name, email: rep.email } : { name: "", email: "", password: "" });
    }
  }, [open, rep, reset]);

  const mutation = useEntityFormMutation<{ name: string; email: string; password?: string }, User>({
    isEdit,
    entityLabel: "sales rep",
    resourceKey: "sales-reps",
    save: (data) =>
      isEdit
        ? salesRepsApi.update(rep!.id, data)
        : salesRepsApi.create(data as { name: string; email: string; password: string }),
    onSaved: () => onOpenChange(false),
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit sales representative" : "New sales representative"}</DialogTitle>
          <DialogDescription>
            {isEdit ? "Update this representative's details." : "Invite a new sales representative to the team."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-4">
          <div>
            <Label htmlFor="name">Full name</Label>
            <Input id="name" {...register("name")} />
            <FieldError message={errors.name?.message} />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" {...register("email")} />
            <FieldError message={errors.email?.message} />
          </div>
          {!isEdit && (
            <div>
              <Label htmlFor="password">Temporary password</Label>
              <Input id="password" type="password" {...register("password")} />
              <FieldError message={errors.password?.message} />
            </div>
          )}
          <DialogFooter>
            <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving..." : isEdit ? "Save changes" : "Create representative"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
