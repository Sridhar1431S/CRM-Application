import { apiClient } from "@/lib/api-client";
import { toQueryParams, type ListParams } from "@/api/types";
import type { Opportunity, OpportunityStage, Paginated } from "@/types";

export type OpportunityInput = Omit<
  Opportunity,
  "id" | "customer_detail" | "assigned_rep_detail" | "created_at" | "updated_at"
>;

export const opportunitiesApi = {
  list: (params?: ListParams) =>
    apiClient.get<Paginated<Opportunity>>("/opportunities/", { params: toQueryParams(params) }).then((r) => r.data),

  get: (id: string) => apiClient.get<Opportunity>(`/opportunities/${id}/`).then((r) => r.data),

  create: (data: OpportunityInput) => apiClient.post<Opportunity>("/opportunities/", data).then((r) => r.data),

  update: (id: string, data: Partial<OpportunityInput>) =>
    apiClient.put<Opportunity>(`/opportunities/${id}/`, data).then((r) => r.data),

  updateStage: (id: string, stage: OpportunityStage) =>
    apiClient.patch<Opportunity>(`/opportunities/${id}/stage/`, { stage }).then((r) => r.data),
};
