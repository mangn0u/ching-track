export interface Category {
  id: number;
  name: string;
  type: "income" | "expense";
  color: string;
  icon: string;
  is_default: boolean;
}

export interface Transaction {
  id: number;
  type: "income" | "expense";
  amount: number;
  currency_code: string;
  category: number | null;
  category_name: string;
  category_color: string;
  category_icon: string;
  date: string;
  note: string;
  mpesa_ref: string;
}

export interface TransactionDetail extends Transaction {
  mpesa_raw_sms: string;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface TransactionFormData {
  type: "income" | "expense";
  amount: number;
  currency_code: string;
  category: number | null;
  date: string;
  note: string;
  mpesa_ref: string;
}

export interface TransactionFilters {
  month?: number;
  year?: number;
  type?: "income" | "expense" | "";
  category?: number;
  currency?: string;
}

export interface TransactionSummary {
  total_income: number;
  total_expense: number;
  net: number;
  savings_rate_pct: number;
  by_category: {
    category: string;
    color: string;
    icon: string;
    amount: number;
    pct: number;
  }[];
}
