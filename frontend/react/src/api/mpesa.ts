import { apiFetch, apiPost } from "./client";
import type { ParseSmsResponse, ConfirmImportPayload, ConfirmImportResponse } from "../types/mpesa";

export function parseSms(rawSms: string): Promise<ParseSmsResponse> {
  return apiPost<ParseSmsResponse>("/api/v1/mpesa/parse-sms/", { raw_sms: rawSms });
}

export function confirmImport(data: ConfirmImportPayload): Promise<ConfirmImportResponse> {
  return apiPost<ConfirmImportResponse>("/api/v1/mpesa/confirm-import/", data);
}
