export interface Bill {
  id: number;
  name: string;
  amount: number;
  currency_code: string;
  due_day: number;
  frequency: "monthly" | "weekly" | "once";
  is_active: boolean;
  next_due_date: string;
  is_paid_this_period: boolean;
}

export interface BillFormData {
  name: string;
  amount: number;
  currency_code: string;
  due_day: number;
  frequency: "monthly" | "weekly" | "once";
}

export interface BillPayment {
  id: number;
  bill: number;
  paid_date: string;
  amount_paid: number;
  note: string;
  created_at: string;
}

export interface PayBillData {
  amount_paid?: number;
  note?: string;
}
