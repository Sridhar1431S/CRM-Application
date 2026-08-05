import { useMutation, useQueryClient, type QueryKey, type UseMutationResult } from "@tanstack/react-query";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api-client";

interface EntityMutationOptions<TData, TVariables> {
  mutationFn: (variables: TVariables) => Promise<TData>;
  /** Query keys invalidated after a successful mutation. */
  invalidateKeys: QueryKey[];
  successTitle: string | ((variables: TVariables) => string);
  errorTitle: string;
  onSuccess?: (data: TData, variables: TVariables) => void;
}

/**
 * Wraps the write pattern shared by every mutation in the app: invalidate the
 * affected queries, show a success toast, and surface API errors through
 * `extractErrorMessage` in an error toast.
 */
export function useEntityMutation<TData, TVariables = void>({
  mutationFn,
  invalidateKeys,
  successTitle,
  errorTitle,
  onSuccess,
}: EntityMutationOptions<TData, TVariables>): UseMutationResult<TData, Error, TVariables> {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation<TData, Error, TVariables>({
    mutationFn,
    onSuccess: (data, variables) => {
      invalidateKeys.forEach((queryKey) => queryClient.invalidateQueries({ queryKey }));
      toast({
        title: typeof successTitle === "function" ? successTitle(variables) : successTitle,
        variant: "success",
      });
      onSuccess?.(data, variables);
    },
    onError: (error) => {
      toast({ title: errorTitle, description: extractErrorMessage(error), variant: "error" });
    },
  });
}

interface EntityFormMutationOptions<TFormValues, TEntity> {
  /** Whether the form is editing an existing record (drives the toast copy). */
  isEdit: boolean;
  /** Lowercase singular label, e.g. "customer" -- used in the toast copy. */
  entityLabel: string;
  /** Root query key for the resource, e.g. "customers". */
  resourceKey: string;
  save: (values: TFormValues) => Promise<TEntity>;
  onSaved: () => void;
}

/**
 * Create/update mutation for the entity form dialogs: refreshes the resource
 * list and the dashboard counters, then closes the dialog.
 */
export function useEntityFormMutation<TFormValues, TEntity>({
  isEdit,
  entityLabel,
  resourceKey,
  save,
  onSaved,
}: EntityFormMutationOptions<TFormValues, TEntity>): UseMutationResult<TEntity, Error, TFormValues> {
  const label = entityLabel.charAt(0).toUpperCase() + entityLabel.slice(1);

  return useEntityMutation<TEntity, TFormValues>({
    mutationFn: save,
    invalidateKeys: [[resourceKey], ["dashboard"]],
    successTitle: `${label} ${isEdit ? "updated" : "created"}`,
    errorTitle: `Couldn't save ${entityLabel}`,
    onSuccess: onSaved,
  });
}
