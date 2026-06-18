import { apiFetch, apiPost, apiPut, apiDelete } from "./client";
import type { Bill, BillFormData, BillPayment, PayBillData } from "../types/bill";

export function fetchBills(active?: boolean): Promise<Bill[]> {
  const qs = active !== undefined ? `?active=${active}` : "";
  return apiFetch<Bill[]>(`/api/v1/bills/${qs}`);
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

export function fetchUpcomingBills(): Promise<Bill[]> {
  return apiFetch<Bill[]>("/api/v1/bills/upcoming/");
}
