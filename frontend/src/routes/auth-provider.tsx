import * as React from "react";
import axios from "axios";
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
      } catch (error) {
        const status = axios.isAxiosError(error) ? error.response?.status : undefined;
        if (status !== 401 && status !== 403) {
          // Not an expired session: the API is unreachable or erroring, which
          // would otherwise look identical to "logged out".
          console.error("Session bootstrap failed", error);
        }
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
