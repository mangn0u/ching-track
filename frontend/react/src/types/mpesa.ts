export interface ParsedTransaction {
  type: "income" | "expense";
  amount: string;
  currency_code: string;
  date: string;
  note: string;
  mpesa_ref: string;
  raw_sms: string;
}

export interface ParseSmsResponse {
  parsed: boolean;
  transaction: ParsedTransaction;
}

export interface ConfirmImportPayload {
  type: "income" | "expense";
  amount: string;
  date: string;
  currency_code: string;
  note: string;
  mpesa_ref: string;
  raw_sms: string;
  category_id: number | null;
}

export interface ConfirmImportResponse {
  id: number;
  type: "income" | "expense";
  amount: string;
  currency_code: string;
  category: number | null;
  date: string;
  note: string;
  mpesa_ref: string;
}
