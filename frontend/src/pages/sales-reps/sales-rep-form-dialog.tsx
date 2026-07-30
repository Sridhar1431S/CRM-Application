import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { salesRepsApi } from "@/api/sales-reps";
import { Button } from "@/components/ui/button";
import { Input, Label, FieldError } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api-client";
import type { User } from "@/types";

const createSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().min(1, "Email is required").email("Enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

const editSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().min(1, "Email is required").email("Enter a valid email address"),
});

interface SalesRepFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  rep?: User | null;
}

export function SalesRepFormDialog({ open, onOpenChange, rep }: SalesRepFormDialogProps) {
  const isEdit = !!rep;
  const queryClient = useQueryClient();
  const { toast } = useToast();

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

  const mutation = useMutation({
    mutationFn: (data: { name: string; email: string; password?: string }) =>
      isEdit ? salesRepsApi.update(rep!.id, data) : salesRepsApi.create(data as { name: string; email: string; password: string }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sales-reps"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast({ title: isEdit ? "Sales rep updated" : "Sales rep created", variant: "success" });
      onOpenChange(false);
    },
    onError: (error) => {
      toast({ title: "Couldn't save sales rep", description: extractErrorMessage(error), variant: "error" });
    },
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
