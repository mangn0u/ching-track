"""Budget URL patterns."""

from django.urls import path
from apps.budgets.views import BudgetListCreateView, BudgetDetailView, BudgetVsActualView

urlpatterns = [
    path("", BudgetListCreateView.as_view(), name="budget-list"),
    path("vs-actual/", BudgetVsActualView.as_view(), name="budget-vs-actual"),
    path("<int:pk>/", BudgetDetailView.as_view(), name="budget-delete"),
]
