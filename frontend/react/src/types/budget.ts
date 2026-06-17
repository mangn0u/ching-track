export interface Budget {
  id: number;
  category: number;
  category_name: string;
  category_color: string;
  month: number;
  year: number;
  limit_amount: number;
}

export interface BudgetFormData {
  category: number;
  month: number;
  year: number;
  limit_amount: number;
}

export interface BudgetVsActual {
  category_id: number;
  category_name: string;
  category_color: string;
  category_icon: string;
  limit: number;
  actual: number;
  remaining: number;
  pct_used: number;
  status: "safe" | "warning" | "over";
}
