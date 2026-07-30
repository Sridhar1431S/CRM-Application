import * as React from "react";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/auth-store";

/**
 * On mount, attempts a silent refresh using the httpOnly cookie. If it
 * succeeds we have a fresh access token and fetch the current user; if it
 * fails, the user simply lands on the login page. This is what makes
 * "persistent authentication after page refresh" work without ever
 * storing a token in localStorage.
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const setAuth = useAuthStore((s) => s.setAuth);
  const setInitializing = useAuthStore((s) => s.setInitializing);

  React.useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const { access } = await authApi.refresh();
        useAuthStore.getState().setAccessToken(access);
        const user = await authApi.me();
        if (!cancelled) setAuth(user, access);
      } catch {
        // No valid session -- that's fine, ProtectedRoute will redirect to /login.
      } finally {
        if (!cancelled) setInitializing(false);
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, [setAuth, setInitializing]);

  return <>{children}</>;
}
