export interface MonthlyTrend {
  month: number;
  year: number;
  income: number;
  expense: number;
  net: number;
}

export interface TopCategory {
  category: string;
  color: string;
  icon: string;
  total: number;
}

export interface TrendsData {
  currency: string;
  monthly: MonthlyTrend[];
  total_income: number;
  total_expense: number;
  net: number;
  top_categories: TopCategory[];
}
