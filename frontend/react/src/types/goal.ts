export interface Goal {
  id: number;
  name: string;
  description: string;
  target_amount: number;
  currency_code: string;
  deadline: string | null;
  created_at: string;
  total_saved: number;
  remaining: number;
  progress_pct: number;
  days_remaining: number | null;
  monthly_required: number | null;
  is_on_track: boolean;
}

export interface GoalFormData {
  name: string;
  description: string;
  target_amount: number;
  currency_code: string;
  deadline: string | null;
}

export interface GoalContribution {
  id: number;
  goal: number;
  amount: number;
  date: string;
  note: string;
  created_at: string;
}

export interface ContributionFormData {
  amount: number;
  date: string;
  note: string;
}
