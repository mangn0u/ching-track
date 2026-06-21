export interface UserPreferences {
  currency: string;
  monthly_spending_limit: number | null;
  updated_at: string;
}

export interface SpendingStatus {
  monthly_limit: number;
  total_spent: number;
  remaining: number;
  pct_used: number;
  status: "safe" | "warning" | "over";
}

export interface PreferenceFormData {
  currency?: string;
  monthly_spending_limit?: number | null;
}
