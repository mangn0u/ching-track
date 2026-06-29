"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/categories/", include("apps.transactions.urls.category_urls")),
    path("api/v1/transactions/", include("apps.transactions.urls.transaction_urls")),
    path("api/v1/budgets/", include("apps.budgets.urls")),
    path("api/v1/preferences/", include("apps.budgets.preference_urls")),
    path("api/v1/bills/", include("apps.bills.urls")),
    path("api/v1/goals/", include("apps.goals.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/mpesa/", include("apps.transactions.urls.mpesa_urls")),

    # OpenAPI schema + Swagger UI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
