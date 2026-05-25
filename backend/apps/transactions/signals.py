"""
Signal: seed default categories when a new user is created.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import CustomUser
from apps.transactions.models import Category

DEFAULT_CATEGORIES = [
    # Income categories
    {"name": "Salary",          "type": "income",  "color": "#22d3ee", "icon": "💼"},
    {"name": "Freelance",       "type": "income",  "color": "#34d399", "icon": "💻"},
    {"name": "Business",        "type": "income",  "color": "#a78bfa", "icon": "🏪"},
    {"name": "Gift",            "type": "income",  "color": "#fb923c", "icon": "🎁"},
    {"name": "M-Pesa Received", "type": "income",  "color": "#4ade80", "icon": "📱"},
    {"name": "Other Income",    "type": "income",  "color": "#94a3b8", "icon": "➕"},
    # Expense categories
    {"name": "Food",            "type": "expense", "color": "#f43f5e", "icon": "🍽️"},
    {"name": "Transport",       "type": "expense", "color": "#f97316", "icon": "🚗"},
    {"name": "Housing",         "type": "expense", "color": "#eab308", "icon": "🏠"},
    {"name": "Utilities",       "type": "expense", "color": "#84cc16", "icon": "💡"},
    {"name": "Health",          "type": "expense", "color": "#ec4899", "icon": "🏥"},
    {"name": "Entertainment",   "type": "expense", "color": "#8b5cf6", "icon": "🎬"},
    {"name": "Shopping",        "type": "expense", "color": "#06b6d4", "icon": "🛍️"},
    {"name": "Education",       "type": "expense", "color": "#3b82f6", "icon": "📚"},
    {"name": "M-Pesa Sent",     "type": "expense", "color": "#10b981", "icon": "📤"},
    {"name": "Other Expense",   "type": "expense", "color": "#6b7280", "icon": "➖"},
]


@receiver(post_save, sender=CustomUser)
def seed_default_categories(sender, instance, created, **kwargs):
    """Create default categories for every new user."""
    if created:
        categories = [
            Category(user=instance, is_default=True, **cat)
            for cat in DEFAULT_CATEGORIES
        ]
        Category.objects.bulk_create(categories)
