"""Goals views — list, CRUD, deposits, and contribution logs."""

from datetime import date
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.goals.models import SavingsGoal, GoalContribution
from apps.goals.serializers import SavingsGoalSerializer, GoalContributionSerializer
from core.permissions import IsOwner

class GoalListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/goals/
    POST /api/v1/goals/
    List all user-scoped goals or create new ones.
    """
    serializer_class = SavingsGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/v1/goals/:id/
    Retrieve, edit, or delete a savings goal.
    """
    serializer_class = SavingsGoalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)


class GoalContributeView(APIView):
    """
    POST /api/v1/goals/:id/contribute/
    Log a deposit towards a specific savings goal.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        user = request.user
        goal = generics.get_object_or_404(SavingsGoal, id=pk, user=user)

        serializer = GoalContributionSerializer(
            data={**request.data, "goal": goal.id},
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Update and return savings goal status
        goal_serializer = SavingsGoalSerializer(goal, context={"request": request})
        return Response(
            {
                "message": "Contribution recorded successfully!",
                "contribution": serializer.data,
                "goal": goal_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class GoalContributionListView(generics.ListAPIView):
    """
    GET /api/v1/goals/:id/contributions/
    Retrieve a paginated listing of contribution records for a specific savings goal.
    """
    serializer_class = GoalContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        goal_id = self.kwargs.get("pk")
        # Ensure the goal exists and belongs to the authenticated user
        generics.get_object_or_404(SavingsGoal, id=goal_id, user=user)
        return GoalContribution.objects.filter(goal_id=goal_id)
