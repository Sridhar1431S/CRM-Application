import { apiClient } from "@/lib/api-client";
import type { AdminDashboardResponse, SalesRepDashboardResponse } from "@/types";

export const dashboardApi = {
  admin: () => apiClient.get<AdminDashboardResponse>("/dashboard/admin").then((r) => r.data),
  salesRep: () => apiClient.get<SalesRepDashboardResponse>("/dashboard/sales-rep").then((r) => r.data),
};
