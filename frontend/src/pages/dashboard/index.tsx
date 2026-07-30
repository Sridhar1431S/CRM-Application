import { useAuthStore } from "@/store/auth-store";
import AdminDashboardPage from "@/pages/dashboard/admin-dashboard-page";
import SalesRepDashboardPage from "@/pages/dashboard/sales-rep-dashboard-page";

export default function DashboardPage() {
  const role = useAuthStore((s) => s.user?.role);
  return role === "admin" ? <AdminDashboardPage /> : <SalesRepDashboardPage />;
}
