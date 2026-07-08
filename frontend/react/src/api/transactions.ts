import { apiFetch, apiPost, apiPut, apiDelete } from "./client";
import type { Transaction, TransactionDetail, TransactionFormData, TransactionFilters, TransactionSummary } from "../types/transaction";

// The backend returns paginated responses: { count, next, previous, results: T[] }
// This helper unwraps the results array.
function unwrapResults<T>(data: unknown): T[] {
  if (data && typeof data === "object" && "results" in data) {
    return (data as { results: T[] }).results;
  }
  return data as T[];
}

export function fetchTransactions(filters?: TransactionFilters): Promise<Transaction[]> {
  const params = new URLSearchParams();
  if (filters?.month) params.set("month", String(filters.month));
  if (filters?.year) params.set("year", String(filters.year));
  if (filters?.type) params.set("type", filters.type);
  if (filters?.category) params.set("category", String(filters.category));
  if (filters?.currency) params.set("currency", filters.currency);
  const qs = params.toString();
  return apiFetch<unknown>(`/api/v1/transactions/${qs ? `?${qs}` : ""}`).then(unwrapResults<Transaction>);
}

export function fetchTransaction(id: number): Promise<TransactionDetail> {
  return apiFetch<TransactionDetail>(`/api/v1/transactions/${id}/`);
}

export function createTransaction(data: TransactionFormData): Promise<Transaction> {
  return apiPost<Transaction>("/api/v1/transactions/", data);
}

export function updateTransaction(id: number, data: Partial<TransactionFormData>): Promise<Transaction> {
  return apiPut<Transaction>(`/api/v1/transactions/${id}/`, data);
}

export function deleteTransaction(id: number): Promise<void> {
  return apiDelete<void>(`/api/v1/transactions/${id}/`);
}

export function fetchTransactionSummary(
  month?: number,
  year?: number,
  currency?: string,
): Promise<TransactionSummary> {
  const params = new URLSearchParams();
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  if (currency) params.set("currency", currency);
  const qs = params.toString();
  return apiFetch<TransactionSummary>(`/api/v1/transactions/summary/${qs ? `?${qs}` : ""}`);
}
