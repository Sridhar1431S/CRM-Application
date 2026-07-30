import { apiClient } from "@/lib/api-client";
import type { User } from "@/types";

export interface LoginResponse {
  access: string;
  user: User;
}

export const authApi = {
  register: (payload: { name: string; email: string; password: string; password_confirm: string; role: "admin" | "sales_rep" }) =>
    apiClient.post<{ user: User; detail: string }> ("/auth/register", payload).then((r) => r.data),

  login: (email: string, password: string) =>
    apiClient.post<LoginResponse>("/auth/login", { email, password }).then((r) => r.data),

  logout: () => apiClient.post("/auth/logout").then((r) => r.data),

  refresh: () => apiClient.post<{ access: string }>("/auth/refresh").then((r) => r.data),

  me: () => apiClient.get<User>("/auth/me").then((r) => r.data),
};
