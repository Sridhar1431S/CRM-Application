import { apiClient } from "@/lib/api-client";
import { toQueryParams, type ListParams } from "@/api/types";
import type { Customer, Paginated } from "@/types";

export type CustomerInput = Omit<Customer, "id" | "created_at" | "updated_at">;

export const customersApi = {
  list: (params?: ListParams) =>
    apiClient.get<Paginated<Customer>>("/customers/", { params: toQueryParams(params) }).then((r) => r.data),

  get: (id: string) => apiClient.get<Customer>(`/customers/${id}/`).then((r) => r.data),

  create: (data: CustomerInput) => apiClient.post<Customer>("/customers/", data).then((r) => r.data),

  update: (id: string, data: Partial<CustomerInput>) =>
    apiClient.put<Customer>(`/customers/${id}/`, data).then((r) => r.data),

  remove: (id: string) => apiClient.delete(`/customers/${id}/`).then((r) => r.data),
};
