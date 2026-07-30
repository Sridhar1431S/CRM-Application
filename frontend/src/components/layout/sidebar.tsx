import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  UserCog,
  Target,
  TrendingUp,
  CalendarClock,
  Settings,
  UserCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["admin", "sales_rep"] },
  { to: "/customers", label: "Customers", icon: Users, roles: ["admin", "sales_rep"] },
  { to: "/leads", label: "Leads", icon: Target, roles: ["admin", "sales_rep"] },
  { to: "/opportunities", label: "Opportunities", icon: TrendingUp, roles: ["admin", "sales_rep"] },
  { to: "/followups", label: "Follow-Ups", icon: CalendarClock, roles: ["admin", "sales_rep"] },
  { to: "/sales-reps", label: "Sales Reps", icon: UserCog, roles: ["admin"] },
];

export function Sidebar() {
  const role = useAuthStore((s) => s.user?.role);

  return (
    <aside className="w-60 shrink-0 flex-col border-r border-border bg-surface/95 max-lg:hidden lg:flex">
      <div className="flex h-14 items-center gap-2 border-b border-border px-5">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white">
          C
        </div>
        <span className="text-sm font-semibold text-ink-900">CRM Lite</span>
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-4">
        {NAV_ITEMS.filter((item) => !role || item.roles.includes(role)).map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                isActive ? "bg-brand-50 text-brand-700 shadow-sm" : "text-ink-500 hover:bg-canvas hover:text-ink-900"
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-border px-3 py-3">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              isActive ? "bg-brand-50 text-brand-700" : "text-ink-500 hover:bg-canvas hover:text-ink-900"
            )
          }
        >
          <Settings className="h-4 w-4" />
          Settings
        </NavLink>
        <NavLink
          to="/profile"
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              isActive ? "bg-brand-50 text-brand-700" : "text-ink-500 hover:bg-canvas hover:text-ink-900"
            )
          }
        >
          <UserCircle className="h-4 w-4" />
          Profile
        </NavLink>
      </div>
    </aside>
  );
}
