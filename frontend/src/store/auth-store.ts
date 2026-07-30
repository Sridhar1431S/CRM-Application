import { create } from "zustand";
import type { User } from "@/types";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isInitializing: boolean;
  setAuth: (user: User, accessToken: string) => void;
  setAccessToken: (accessToken: string) => void;
  clearAuth: () => void;
  setInitializing: (value: boolean) => void;
}

/**
 * Access token lives only in memory (this store), never localStorage --
 * that's what protects it from XSS-based token theft. The refresh token
 * lives in an httpOnly cookie the JS layer never touches directly.
 *
 * "Persistent login after page refresh" is achieved by AuthProvider calling
 * POST /auth/refresh on app mount, which succeeds as long as the refresh
 * cookie is still valid -- no token needs to survive in browser storage.
 */
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  isInitializing: true,
  setAuth: (user, accessToken) => set({ user, accessToken }),
  setAccessToken: (accessToken) => set({ accessToken }),
  clearAuth: () => set({ user: null, accessToken: null }),
  setInitializing: (value) => set({ isInitializing: value }),
}));
