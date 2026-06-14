export interface DashboardSummary {
  total_income: number;
  total_expense: number;
  net: number;
  savings_rate_pct: number;
}

export interface CategorySpending {
  category: string;
  color: string;
  icon: string;
  amount: number;
  pct: number;
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

export interface GlobalLimit {
  monthly_limit: number;
  total_spent: number;
  remaining: number;
  pct_used: number;
  status: "safe" | "warning" | "over";
}

export interface UpcomingBill {
  id: number;
  name: string;
  amount: number;
  currency_code: string;
  due_day: number;
  frequency: string;
  next_due_date: string;
  is_paid_this_period: boolean;
}

export interface GoalSnapshot {
  id: number;
  name: string;
  target_amount: number;
  total_saved: number;
  progress_pct: number;
  is_on_track: boolean;
  currency_code: string;
}

export interface MomChange {
  income_change_pct: number;
  expense_change_pct: number;
}

export interface DashboardData {
  month: number;
  year: number;
  currency: string;
  summary: DashboardSummary;
  spending_by_category: CategorySpending[];
  budget_vs_actual: BudgetVsActual[];
  global_limit: GlobalLimit;
  upcoming_bills: UpcomingBill[];
  goals: GoalSnapshot[];
  mom_change: MomChange;
}
