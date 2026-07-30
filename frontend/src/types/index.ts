export type Role = "admin" | "sales_rep";

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  is_active: boolean;
  created_at: string;
}

export type CustomerStatus = "prospect" | "active" | "inactive";

export interface Customer {
  id: string;
  company_name: string;
  contact_person: string;
  email: string;
  phone_number: string;
  industry: string;
  status: CustomerStatus;
  created_at: string;
  updated_at: string;
}

export type LeadPriority = "low" | "medium" | "high";
export type LeadStatus = "new" | "contacted" | "qualified" | "lost";

export interface Lead {
  id: string;
  company_name: string;
  contact_name: string;
  email: string;
  phone_number: string;
  source: string;
  priority: LeadPriority;
  status: LeadStatus;
  assigned_rep: string | null;
  assigned_rep_detail: User | null;
  converted_to_opportunity: boolean;
  created_at: string;
  updated_at: string;
}

export type OpportunityStage = "qualification" | "proposal" | "negotiation" | "won" | "lost";

export interface Opportunity {
  id: string;
  customer: string;
  customer_detail: Customer;
  assigned_rep: string | null;
  assigned_rep_detail: User | null;
  estimated_value: string;
  expected_closing_date: string;
  stage: OpportunityStage;
  created_at: string;
  updated_at: string;
}

export interface FollowUp {
  id: string;
  opportunity: string;
  note: string;
  next_followup_date: string | null;
  created_by: string | null;
  created_by_detail: User | null;
  created_at: string;
}

export interface Paginated<T> {
  count: number;
  total_pages: number;
  current_page: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AdminDashboardSummary {
  total_customers: number;
  total_leads: number;
  open_opportunities: number;
  active_sales_representatives: number;
}

export interface ProgressMonitoringRow {
  opportunity_id: string;
  customer: string;
  sales_representative: string | null;
  stage: OpportunityStage;
  value: string;
  expected_close: string;
}

export interface AdminDashboardResponse {
  summary: AdminDashboardSummary;
  progress_monitoring: ProgressMonitoringRow[];
}

export interface SalesRepDashboardResponse {
  assigned_customers: number;
  assigned_leads: number;
  open_opportunities: number;
  followups_due_today: number;
}

export interface ApiErrorPayload {
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}
