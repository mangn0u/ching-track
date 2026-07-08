import { apiFetch, apiPost, apiPut, apiDelete } from "./client";
import type { Goal, GoalFormData, GoalContribution, ContributionFormData } from "../types/goal";

function unwrapResults<T>(data: unknown): T[] {
  if (data && typeof data === "object" && "results" in data) {
    return (data as { results: T[] }).results;
  }
  return data as T[];
}

export function fetchGoals(): Promise<Goal[]> {
  return apiFetch<unknown>("/api/v1/goals/").then(unwrapResults<Goal>);
}

export function createGoal(data: GoalFormData): Promise<Goal> {
  return apiPost<Goal>("/api/v1/goals/", data);
}

export function updateGoal(id: number, data: Partial<GoalFormData>): Promise<Goal> {
  return apiPut<Goal>(`/api/v1/goals/${id}/`, data);
}

export function deleteGoal(id: number): Promise<void> {
  return apiDelete<void>(`/api/v1/goals/${id}/`);
}

export function contributeToGoal(id: number, data: ContributionFormData): Promise<{
  message: string;
  contribution: GoalContribution;
  goal: Goal;
}> {
  return apiPost<{
    message: string;
    contribution: GoalContribution;
    goal: Goal;
  }>(`/api/v1/goals/${id}/contribute/`, data);
}

export function fetchContributions(goalId: number): Promise<GoalContribution[]> {
  return apiFetch<unknown>(`/api/v1/goals/${goalId}/contributions/`).then(unwrapResults<GoalContribution>);
}
