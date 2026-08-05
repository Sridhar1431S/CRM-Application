import * as React from "react";
import { useNavigate } from "react-router-dom";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { ChevronDown, LogOut, Menu, Moon, Settings, Sun, UserCircle, X } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/auth-store";
import { initials, cn } from "@/lib/utils";
import { Sidebar } from "@/components/layout/sidebar";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api-client";

export function Navbar({ title }: { title?: string }) {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const { toast } = useToast();
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [theme, setTheme] = React.useState<"light" | "dark">(() => {
    if (typeof window === "undefined") return "light";
    return window.localStorage.getItem("crm-theme") === "dark" ? "dark" : "light";
  });

  React.useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    document.documentElement.style.colorScheme = theme;
    window.localStorage.setItem("crm-theme", theme);
  }, [theme]);

  const logoutMutation = useMutation({
    mutationFn: authApi.logout,
    onSettled: (_data, error) => {
      clearAuth();
      navigate("/login", { replace: true });
      if (error) {
        toast({
          title: "Signed out on this device only",
          description: `${extractErrorMessage(error)} Your session may still be active on the server.`,
          variant: "error",
        });
      } else {
        toast({ title: "Logged out", variant: "info" });
      }
    },
  });

  return (
    <>
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-surface px-4 lg:px-6">
        <div className="flex items-center gap-3">
          <button
            className="rounded-lg p-2 text-ink-500 transition hover:bg-canvas hover:text-ink-800 lg:hidden"
            onClick={() => setMobileOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </button>
          <h1 className="text-sm font-semibold text-ink-900">{title}</h1>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className="rounded-lg p-2 text-ink-500 transition hover:bg-canvas"
            onClick={() => setTheme((value) => (value === "dark" ? "light" : "dark"))}
            aria-label="Toggle color theme"
          >
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>

          <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button className="flex items-center gap-2 rounded-lg px-2 py-1.5 transition hover:bg-canvas hover:shadow-sm">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                {user ? initials(user.name) : "?"}
              </div>
              <div className="max-sm:hidden text-left sm:block">
                <p className="text-xs font-medium text-ink-900">{user?.name}</p>
                <p className="text-[11px] capitalize text-ink-400">{user?.role.replace("_", " ")}</p>
              </div>
              <ChevronDown className="h-3.5 w-3.5 text-ink-400" />
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content
              align="end"
              sideOffset={8}
              className="z-50 w-48 rounded-lg border border-border bg-surface p-1 shadow-[var(--shadow-popover)]"
            >
              <DropdownMenu.Item
                className="flex cursor-pointer items-center gap-2 rounded-md px-2.5 py-2 text-sm text-ink-700 outline-none hover:bg-canvas"
                onSelect={() => navigate("/profile")}
              >
                <UserCircle className="h-4 w-4" /> Profile
              </DropdownMenu.Item>
              <DropdownMenu.Item
                className="flex cursor-pointer items-center gap-2 rounded-md px-2.5 py-2 text-sm text-ink-700 outline-none hover:bg-canvas"
                onSelect={() => navigate("/settings")}
              >
                <Settings className="h-4 w-4" /> Settings
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="my-1 h-px bg-border" />
              <DropdownMenu.Item
                className="flex cursor-pointer items-center gap-2 rounded-md px-2.5 py-2 text-sm text-danger-600 outline-none hover:bg-danger-50"
                onSelect={() => logoutMutation.mutate()}
              >
                <LogOut className="h-4 w-4" /> Log out
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
        </div>
      </header>

      <DialogPrimitive.Root open={mobileOpen} onOpenChange={setMobileOpen}>
        <DialogPrimitive.Portal>
          <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-ink-900/40 lg:hidden" />
          <DialogPrimitive.Content
            className={cn(
              "fixed left-0 top-0 z-50 h-full w-64 bg-surface shadow-[var(--shadow-popover)] lg:hidden",
              "data-[state=open]:animate-in data-[state=open]:slide-in-from-left"
            )}
          >
            <DialogPrimitive.Title className="sr-only">Navigation</DialogPrimitive.Title>
            <div className="flex justify-end p-3">
              <DialogPrimitive.Close className="rounded-md p-1.5 text-ink-500 hover:bg-canvas">
                <X className="h-5 w-5" />
              </DialogPrimitive.Close>
            </div>
            <div className="[&>aside]:flex [&>aside]:w-full [&>aside]:border-0">
              <Sidebar />
            </div>
          </DialogPrimitive.Content>
        </DialogPrimitive.Portal>
      </DialogPrimitive.Root>
    </>
  );
}
