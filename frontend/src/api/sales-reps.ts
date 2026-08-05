import { apiClient } from "@/lib/api-client";
import { createResourceApi } from "@/api/resource";
import type { User } from "@/types";

export interface SalesRepInput {
  name: string;
  email: string;
  password?: string;
  is_active?: boolean;
}

const resource = createResourceApi<User, SalesRepInput>("sales-reps");

export const salesRepsApi = {
  list: resource.list,
  get: resource.get,
  create: resource.create,
  update: resource.update,

  disable: (id: string) => apiClient.patch<User>(`/sales-reps/${id}/disable/`).then((r) => r.data),

  enable: (id: string) => apiClient.patch<User>(`/sales-reps/${id}/enable/`).then((r) => r.data),
};
