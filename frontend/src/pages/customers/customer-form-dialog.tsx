import { useEffect } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { customersApi } from "@/api/customers";
import { Button } from "@/components/ui/button";
import { Input, Label, FieldError, Select } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api-client";
import type { Customer } from "@/types";

const schema = z.object({
  company_name: z.string().min(1, "Company name is required"),
  contact_person: z.string().min(1, "Contact person is required"),
  email: z.string().min(1, "Email is required").email("Enter a valid email address"),
  phone_number: z
    .string()
    .min(7, "Enter a valid phone number")
    .regex(/^\+?[0-9\s\-()]{7,20}$/, "Enter a valid phone number"),
  industry: z.string().optional(),
  status: z.enum(["prospect", "active", "inactive"]),
});

type FormValues = z.infer<typeof schema>;

interface CustomerFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  customer?: Customer | null;
}

export function CustomerFormDialog({ open, onOpenChange, customer }: CustomerFormDialogProps) {
  const isEdit = !!customer;
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { status: "prospect", industry: "" },
  });

  useEffect(() => {
    if (open) {
      reset(
        customer
          ? {
              company_name: customer.company_name,
              contact_person: customer.contact_person,
              email: customer.email,
              phone_number: customer.phone_number,
              industry: customer.industry ?? "",
              status: customer.status,
            }
          : { company_name: "", contact_person: "", email: "", phone_number: "", industry: "", status: "prospect" }
      );
    }
  }, [open, customer, reset]);

  const mutation = useMutation({
    mutationFn: (data: FormValues) =>
      isEdit ? customersApi.update(customer!.id, data) : customersApi.create(data as Customer),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast({ title: isEdit ? "Customer updated" : "Customer created", variant: "success" });
      onOpenChange(false);
    },
    onError: (error) => {
      toast({ title: "Couldn't save customer", description: extractErrorMessage(error), variant: "error" });
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit customer" : "New customer"}</DialogTitle>
          <DialogDescription>
            {isEdit ? "Update this customer's details." : "Add a new customer to your CRM."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="company_name">Company name</Label>
              <Input id="company_name" {...register("company_name")} />
              <FieldError message={errors.company_name?.message} />
            </div>
            <div>
              <Label htmlFor="contact_person">Contact person</Label>
              <Input id="contact_person" {...register("contact_person")} />
              <FieldError message={errors.contact_person?.message} />
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
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="industry">Industry</Label>
              <Input id="industry" placeholder="e.g. SaaS" {...register("industry")} />
            </div>
            <div>
              <Label htmlFor="status">Status</Label>
              <Controller
                control={control}
                name="status"
                render={({ field }) => (
                  <Select id="status" {...field}>
                    <option value="prospect">Prospect</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
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
              {mutation.isPending ? "Saving..." : isEdit ? "Save changes" : "Create customer"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
