import { apiClient } from "@/lib/api-client";
import { toQueryParams, type ListParams } from "@/api/types";
import type { Paginated } from "@/types";

export interface ResourceApi<T, TInput> {
  list: (params?: ListParams) => Promise<Paginated<T>>;
  get: (id: string) => Promise<T>;
  create: (data: TInput) => Promise<T>;
  update: (id: string, data: Partial<TInput>) => Promise<T>;
  remove: (id: string) => Promise<unknown>;
}

/**
 * Builds the standard CRUD calls for a DRF ViewSet mounted at `/{basePath}/`.
 * Resources pick the operations their endpoint actually exposes and add their
 * own sub-actions (e.g. /assign, /stage) alongside them.
 */
export function createResourceApi<T, TInput>(basePath: string): ResourceApi<T, TInput> {
  const collectionUrl = `/${basePath}/`;
  const detailUrl = (id: string) => `/${basePath}/${id}/`;

  return {
    list: (params) =>
      apiClient.get<Paginated<T>>(collectionUrl, { params: toQueryParams(params) }).then((r) => r.data),

    get: (id) => apiClient.get<T>(detailUrl(id)).then((r) => r.data),

    create: (data) => apiClient.post<T>(collectionUrl, data).then((r) => r.data),

    update: (id, data) => apiClient.put<T>(detailUrl(id), data).then((r) => r.data),

    remove: (id) => apiClient.delete(detailUrl(id)).then((r) => r.data),
  };
}
