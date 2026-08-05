import { createResourceApi } from "@/api/resource";
import type { Customer } from "@/types";

export type CustomerInput = Omit<Customer, "id" | "created_at" | "updated_at">;

export const customersApi = createResourceApi<Customer, CustomerInput>("customers");
