import { create } from "zustand";
import type { MockUser } from "@/lib/mock-data";

interface AuthState {
  user: MockUser | null;
  isAuthenticated: boolean;
  setUser: (user: MockUser | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  // NextAuth 세션 기반으로 초기화 — SessionProvider + useSession()으로 동기화
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  logout: () => set({ user: null, isAuthenticated: false }),
}));
