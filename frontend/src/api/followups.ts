import { apiClient } from "@/lib/api-client";
import { toQueryParams, type ListParams } from "@/api/types";
import type { FollowUp, Paginated } from "@/types";

export const followupsApi = {
  listForOpportunity: (opportunityId: string, params?: ListParams) =>
    apiClient
      .get<Paginated<FollowUp>>(`/opportunities/${opportunityId}/followups`, { params: toQueryParams(params) })
      .then((r) => r.data),

  create: (opportunityId: string, data: { note: string; next_followup_date?: string | null }) =>
    apiClient.post<FollowUp>(`/opportunities/${opportunityId}/followups`, data).then((r) => r.data),

  upcoming: () => apiClient.get<FollowUp[]>("/followups/upcoming").then((r) => r.data),
};
