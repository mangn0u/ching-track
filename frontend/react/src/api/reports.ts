import { apiFetch } from "./client";
import type { TrendsData } from "../types/reports";

export function fetchTrends(months = 6): Promise<TrendsData> {
  return apiFetch<TrendsData>(`/api/v1/analytics/trends/?months=${months}`);
}
