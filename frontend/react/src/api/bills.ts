import { apiFetch, apiPost, apiPut, apiDelete } from "./client";
import type { Bill, BillFormData, BillPayment, PayBillData } from "../types/bill";

function unwrapResults<T>(data: unknown): T[] {
  if (data && typeof data === "object" && "results" in data) {
    return (data as { results: T[] }).results;
  }
  return data as T[];
}

export function fetchBills(active?: boolean): Promise<Bill[]> {
  const qs = active !== undefined ? `?active=${active}` : "";
  return apiFetch<unknown>(`/api/v1/bills/${qs}`).then(unwrapResults<Bill>);
}

export function createBill(data: BillFormData): Promise<Bill> {
  return apiPost<Bill>("/api/v1/bills/", data);
}

export function updateBill(id: number, data: Partial<BillFormData>): Promise<Bill> {
  return apiPut<Bill>(`/api/v1/bills/${id}/`, data);
}

export function deleteBill(id: number): Promise<void> {
  return apiDelete<void>(`/api/v1/bills/${id}/`);
}

export function payBill(id: number, data: PayBillData): Promise<BillPayment> {
  return apiPost<BillPayment>(`/api/v1/bills/${id}/pay/`, data);
}


