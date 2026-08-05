import { apiClient } from "@/lib/api-client";
import { createResourceApi } from "@/api/resource";
import type { Opportunity, OpportunityStage } from "@/types";

export type OpportunityInput = Omit<
  Opportunity,
  "id" | "customer_detail" | "assigned_rep_detail" | "created_at" | "updated_at"
>;

const resource = createResourceApi<Opportunity, OpportunityInput>("opportunities");

export const opportunitiesApi = {
  list: resource.list,
  get: resource.get,
  create: resource.create,
  update: resource.update,

  updateStage: (id: string, stage: OpportunityStage) =>
    apiClient.patch<Opportunity>(`/opportunities/${id}/stage/`, { stage }).then((r) => r.data),
};
