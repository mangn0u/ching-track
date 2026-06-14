import { apiFetch } from "./client";
import type { DashboardData } from "../types/dashboard";

export function fetchDashboard(
  month?: number,
  year?: number,
): Promise<DashboardData> {
  const params = new URLSearchParams();
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  const qs = params.toString();
  return apiFetch<DashboardData>(`/api/v1/analytics/dashboard/${qs ? `?${qs}` : ""}`);
}
