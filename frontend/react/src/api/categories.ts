import { apiFetch, apiPost, apiPut, apiDelete } from "./client";
import type { Category } from "../types/transaction";
import type { CategoryFormData } from "../types/category";

export function fetchCategories(type?: string): Promise<Category[]> {
  const qs = type ? `?type=${type}` : "";
  return apiFetch<unknown>(`/api/v1/categories/${qs}`).then(unwrapResults<Category>);
}

function unwrapResults<T>(data: unknown): T[] {
  if (data && typeof data === "object" && "results" in data) {
    return (data as { results: T[] }).results;
  }
  return data as T[];
}

export function createCategory(data: CategoryFormData): Promise<Category> {
  return apiPost<Category>("/api/v1/categories/", data);
}

export function updateCategory(id: number, data: Partial<CategoryFormData>): Promise<Category> {
  return apiPut<Category>(`/api/v1/categories/${id}/`, data);
}

export function deleteCategory(id: number): Promise<void> {
  return apiDelete<void>(`/api/v1/categories/${id}/`);
}
