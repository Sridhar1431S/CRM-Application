import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "@/components/layout/sidebar";
import { Navbar } from "@/components/layout/navbar";

const PAGE_TITLES: { pattern: RegExp; title: string }[] = [
  { pattern: /^\/dashboard/, title: "Dashboard" },
  { pattern: /^\/customers/, title: "Customers" },
  { pattern: /^\/leads/, title: "Leads" },
  { pattern: /^\/opportunities\/[^/]+$/, title: "Opportunity" },
  { pattern: /^\/opportunities/, title: "Opportunities" },
  { pattern: /^\/followups/, title: "Follow-Ups" },
  { pattern: /^\/sales-reps/, title: "Sales Representatives" },
  { pattern: /^\/profile/, title: "Profile" },
  { pattern: /^\/settings/, title: "Settings" },
];

function getTitleForPath(pathname: string): string {
  return PAGE_TITLES.find((entry) => entry.pattern.test(pathname))?.title ?? "";
}

export function AppLayout() {
  const location = useLocation();
  const title = getTitleForPath(location.pathname);

  return (
    <div className="flex min-h-screen bg-canvas text-ink-900">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar title={title} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-3 sm:p-4 lg:p-6">
          <div className="mx-auto w-full max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}