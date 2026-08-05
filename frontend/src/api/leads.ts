import { apiClient } from "@/lib/api-client";
import { createResourceApi } from "@/api/resource";
import type { Lead, Opportunity } from "@/types";

export type LeadInput = Omit<
  Lead,
  "id" | "assigned_rep_detail" | "converted_to_opportunity" | "created_at" | "updated_at"
>;

const resource = createResourceApi<Lead, LeadInput>("leads");

export const leadsApi = {
  ...resource,

  assign: (id: string, assigned_rep: string) =>
    apiClient.post<Lead>(`/leads/${id}/assign/`, { assigned_rep }).then((r) => r.data),

  convert: (id: string, data: { estimated_value: string; expected_closing_date: string }) =>
    apiClient.post<Opportunity>(`/leads/${id}/convert/`, data).then((r) => r.data),
};
