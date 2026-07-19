const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Role = "admin" | "engineer" | "viewer";
export type AP = "H" | "M" | "L";

export interface Project {
  id: string;
  name: string;
  customer: string;
  fmea_number: string;
  revision: string;
  intent: string;
  team: string;
  locale: string;
  is_baseline: boolean;
}

export interface Me {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  organization_id: string;
}

const TOKEN_KEY = "pfmea_token";

export const auth = {
  get token() {
    return sessionStorage.getItem(TOKEN_KEY);
  },
  set token(value: string | null) {
    if (value) sessionStorage.setItem(TOKEN_KEY, value);
    else sessionStorage.removeItem(TOKEN_KEY);
  },
};

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (auth.token) headers.set("Authorization", `Bearer ${auth.token}`);
  if (init.body && !(init.body instanceof URLSearchParams)) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(`${BASE}${path}`, { ...init, headers });
  if (!res.ok) throw new Error((await res.text()) || res.statusText);
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

export const api = {
  async login(email: string, password: string) {
    const body = new URLSearchParams({ username: email, password });
    const data = await request<{ access_token: string }>("/api/auth/login", {
      method: "POST",
      body,
    });
    auth.token = data.access_token;
    return data;
  },
  me: () => request<Me>("/api/auth/me"),
  listProjects: () => request<Project[]>("/api/projects"),
  createProject: (payload: Partial<Project>) =>
    request<Project>("/api/projects", { method: "POST", body: JSON.stringify(payload) }),
  actionPriority: (severity: number, occurrence: number, detection: number) =>
    request<{ action_priority: AP }>("/api/risk/action-priority", {
      method: "POST",
      body: JSON.stringify({ severity, occurrence, detection }),
    }),
};
