import { apiFetch, apiPost, apiDelete } from "./client";
import type { Budget, BudgetFormData, BudgetVsActual } from "../types/budget";

function unwrapResults<T>(data: unknown): T[] {
  if (data && typeof data === "object" && "results" in data) {
    return (data as { results: T[] }).results;
  }
  return data as T[];
}

export function fetchBudgets(month?: number, year?: number): Promise<Budget[]> {
  const params = new URLSearchParams();
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  const qs = params.toString();
  return apiFetch<unknown>(`/api/v1/budgets/${qs ? `?${qs}` : ""}`).then(unwrapResults<Budget>);
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
  return apiFetch<unknown>(`/api/v1/budgets/vs-actual/${qs ? `?${qs}` : ""}`).then(unwrapResults<BudgetVsActual>);
}
