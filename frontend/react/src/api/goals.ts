import { apiFetch, apiPost, apiPut, apiDelete } from "./client";
import type { Goal, GoalFormData, GoalContribution, ContributionFormData } from "../types/goal";

export function fetchGoals(): Promise<Goal[]> {
  return apiFetch<Goal[]>("/api/v1/goals/");
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
  return apiFetch<GoalContribution[]>(`/api/v1/goals/${goalId}/contributions/`);
}
