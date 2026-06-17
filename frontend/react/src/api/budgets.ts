import { apiFetch, apiPost, apiDelete } from "./client";
import type { Budget, BudgetFormData, BudgetVsActual } from "../types/budget";

export function fetchBudgets(month?: number, year?: number): Promise<Budget[]> {
  const params = new URLSearchParams();
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  const qs = params.toString();
  return apiFetch<Budget[]>(`/api/v1/budgets/${qs ? `?${qs}` : ""}`);
}

export function upsertBudget(data: BudgetFormData): Promise<Budget> {
  return apiPost<Budget>("/api/v1/budgets/", data);
}

export function deleteBudget(id: number): Promise<void> {
  return apiDelete<void>(`/api/v1/budgets/${id}/`);
}

export function fetchBudgetVsActual(month?: number, year?: number): Promise<BudgetVsActual[]> {
  const params = new URLSearchParams();
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  const qs = params.toString();
  return apiFetch<BudgetVsActual[]>(`/api/v1/budgets/vs-actual/${qs ? `?${qs}` : ""}`);
}
