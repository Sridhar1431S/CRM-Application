import { apiClient } from "@/lib/api-client";
import { toQueryParams, type ListParams } from "@/api/types";
import type { Lead, Opportunity, Paginated } from "@/types";

export type LeadInput = Omit<
  Lead,
  "id" | "assigned_rep_detail" | "converted_to_opportunity" | "created_at" | "updated_at"
>;

export const leadsApi = {
  list: (params?: ListParams) =>
    apiClient.get<Paginated<Lead>>("/leads/", { params: toQueryParams(params) }).then((r) => r.data),

  get: (id: string) => apiClient.get<Lead>(`/leads/${id}/`).then((r) => r.data),

  create: (data: LeadInput) => apiClient.post<Lead>("/leads/", data).then((r) => r.data),

  update: (id: string, data: Partial<LeadInput>) =>
    apiClient.put<Lead>(`/leads/${id}/`, data).then((r) => r.data),

  remove: (id: string) => apiClient.delete(`/leads/${id}/`).then((r) => r.data),

  assign: (id: string, assigned_rep: string) =>
    apiClient.post<Lead>(`/leads/${id}/assign/`, { assigned_rep }).then((r) => r.data),

  convert: (id: string, data: { estimated_value: string; expected_closing_date: string }) =>
    apiClient.post<Opportunity>(`/leads/${id}/convert/`, data).then((r) => r.data),
};
