import { apiFetch, apiPost, setTokens } from "./client";

export interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  mpesa_phone: string | null;
  is_email_verified: boolean;
  date_joined: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: UserProfile;
}

export function login(email: string, password: string): Promise<LoginResponse> {
  return apiPost<LoginResponse>("/api/v1/auth/login/", { email, password });
}

export function fetchMe(): Promise<UserProfile> {
  return apiFetch<UserProfile>("/api/v1/auth/me/");
}

export async function loginAndStore(
  email: string,
  password: string,
): Promise<UserProfile> {
  const data = await login(email, password);
  setTokens(data.access, data.refresh);
  return data.user;
}

export interface RegisterPayload {
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  mpesa_phone?: string;
}

export function register(payload: RegisterPayload): Promise<UserProfile> {
  return apiPost<UserProfile>("/api/v1/auth/register/", payload);
}

export interface ForgotPasswordPayload {
  email: string;
}

export function forgotPassword(payload: ForgotPasswordPayload): Promise<{ message: string }> {
  return apiPost<{ message: string }>("/api/v1/auth/forgot-password/", payload);
}

export function resetPassword(token: string, password: string): Promise<{ message: string }> {
  return apiPost<{ message: string }>(`/api/v1/auth/reset-password/${token}/`, { password });
}

export interface ChangePasswordPayload {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}

export function changePassword(payload: ChangePasswordPayload): Promise<{ message: string }> {
  return apiPost<{ message: string }>("/api/v1/auth/change-password/", payload);
}
