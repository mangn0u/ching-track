import { apiFetch, apiPut } from "./client";
import type { UserPreferences, PreferenceFormData, SpendingStatus } from "../types/preferences";

export function fetchPreferences(): Promise<UserPreferences> {
  return apiFetch<UserPreferences>("/api/v1/preferences/");
}

export function updatePreferences(data: PreferenceFormData): Promise<UserPreferences> {
  return apiPut<UserPreferences>("/api/v1/preferences/", data);
}

export function fetchSpendingStatus(month?: number, year?: number): Promise<SpendingStatus> {
  const params = new URLSearchParams();
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  const qs = params.toString();
  return apiFetch<SpendingStatus>(`/api/v1/preferences/spending-status/${qs ? `?${qs}` : ""}`);
}
