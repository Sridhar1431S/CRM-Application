import { apiClient } from "@/lib/api-client";
import { toQueryParams, type ListParams } from "@/api/types";
import type { Paginated, User } from "@/types";

export interface SalesRepInput {
  name: string;
  email: string;
  password?: string;
  is_active?: boolean;
}

export const salesRepsApi = {
  list: (params?: ListParams) =>
    apiClient.get<Paginated<User>>("/sales-reps/", { params: toQueryParams(params) }).then((r) => r.data),

  get: (id: string) => apiClient.get<User>(`/sales-reps/${id}/`).then((r) => r.data),

  create: (data: SalesRepInput) => apiClient.post<User>("/sales-reps/", data).then((r) => r.data),

  update: (id: string, data: Partial<SalesRepInput>) =>
    apiClient.put<User>(`/sales-reps/${id}/`, data).then((r) => r.data),

  disable: (id: string) => apiClient.patch<User>(`/sales-reps/${id}/disable/`).then((r) => r.data),

  enable: (id: string) => apiClient.patch<User>(`/sales-reps/${id}/enable/`).then((r) => r.data),
};
