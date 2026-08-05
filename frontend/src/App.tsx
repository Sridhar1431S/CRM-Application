import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ToastProvider } from "@/components/ui/toast";
import { ErrorBoundary } from "@/components/shared/error-boundary";
import { AuthProvider } from "@/routes/auth-provider";
import { ProtectedRoute, GuestRoute } from "@/routes/protected-route";
import { AppLayout } from "@/components/layout/app-layout";

import LandingPage from "@/pages/landing/landing-page";
import LoginPage from "@/pages/auth/login-page";
import DashboardPage from "@/pages/dashboard";
import CustomersPage from "@/pages/customers/customers-page";
import SalesRepsPage from "@/pages/sales-reps/sales-reps-page";
import LeadsPage from "@/pages/leads/leads-page";
import OpportunitiesPage from "@/pages/opportunities/opportunities-page";
import OpportunityDetailPage from "@/pages/opportunities/opportunity-detail-page";
import FollowUpsPage from "@/pages/followups/followups-page";
import ProfilePage from "@/pages/profile/profile-page";
import SettingsPage from "@/pages/settings/settings-page";
import NotFoundPage from "@/pages/not-found-page";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <BrowserRouter>
            <AuthProvider>
              <Routes>
                <Route element={<GuestRoute />}>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/login" element={<LoginPage />} />
                </Route>

                <Route element={<ProtectedRoute />}>
                  <Route element={<AppLayout />}>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={<DashboardPage />} handle={{ title: "Dashboard" }} />
                    <Route path="/customers" element={<CustomersPage />} handle={{ title: "Customers" }} />
                    <Route path="/leads" element={<LeadsPage />} handle={{ title: "Leads" }} />
                    <Route path="/opportunities" element={<OpportunitiesPage />} handle={{ title: "Opportunities" }} />
                    <Route
                      path="/opportunities/:id"
                      element={<OpportunityDetailPage />}
                      handle={{ title: "Opportunity" }}
                    />
                    <Route path="/followups" element={<FollowUpsPage />} handle={{ title: "Follow-Ups" }} />
                    <Route path="/profile" element={<ProfilePage />} handle={{ title: "Profile" }} />
                    <Route path="/settings" element={<SettingsPage />} handle={{ title: "Settings" }} />

                    <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
                      <Route path="/sales-reps" element={<SalesRepsPage />} handle={{ title: "Sales Representatives" }} />
                    </Route>
                  </Route>
                </Route>

                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </AuthProvider>
          </BrowserRouter>
        </ToastProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
