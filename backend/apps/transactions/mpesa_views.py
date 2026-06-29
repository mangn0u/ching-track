"""M-Pesa SMS parsing views — parse SMS text and confirm transaction import."""

from datetime import date
from html import escape

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.transactions.models import Transaction
from apps.transactions.mpesa_parser import parse_mpesa_sms


class ParseSmsView(APIView):
    """
    POST /api/v1/mpesa/parse-sms/
    Accept raw M-Pesa SMS text, parse it, and return a pre-filled transaction.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        raw_sms = request.data.get("raw_sms", "").strip()

        if not raw_sms:
            return Response(
                {"error": "raw_sms field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(raw_sms) > 1000:
            return Response(
                {"error": "SMS text too long (max 1000 characters)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = parse_mpesa_sms(raw_sms)

        if result is None:
            return Response(
                {"error": "Could not parse this SMS. Make sure it is a valid M-Pesa message."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response({
            "parsed": True,
            "transaction": result,
        }, status=status.HTTP_200_OK)


class ConfirmImportView(APIView):
    """
    POST /api/v1/mpesa/confirm-import/
    Confirm and create a transaction from parsed M-Pesa data.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        required = ("type", "amount", "date")
        missing = [f for f in required if not data.get(f)]
        if missing:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tx_type = data.get("type")
        if tx_type not in ("income", "expense"):
            return Response(
                {"error": "type must be 'income' or 'expense'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = float(data["amount"])
        except (ValueError, TypeError):
            return Response(
                {"error": "amount must be a valid number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if amount <= 0:
            return Response(
                {"error": "amount must be greater than zero."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        category_id = data.get("category_id")
        if category_id is not None:
            from apps.transactions.models import Category
            try:
                category = Category.objects.get(id=category_id, user=user)
                if category.type != tx_type:
                    return Response(
                        {"error": f"Selected category type must be '{tx_type}'."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Category.DoesNotExist:
                return Response(
                    {"error": "Category not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            category = None

        note = escape(data.get("note", ""), quote=False)[:255]
        mpesa_ref = data.get("mpesa_ref", "")[:20]
        raw_sms = escape(data.get("raw_sms", ""), quote=False)

        if mpesa_ref and Transaction.objects.filter(user=user, mpesa_ref=mpesa_ref).exists():
            return Response(
                {"error": "A transaction with this M-Pesa reference already exists."},
                status=status.HTTP_409_CONFLICT,
            )

        tx_date_str = data["date"]
        try:
            tx_date = date.fromisoformat(tx_date_str)
        except (ValueError, TypeError):
            return Response(
                {"error": "date must be in YYYY-MM-DD format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transaction = Transaction.objects.create(
            user=user,
            type=tx_type,
            amount=amount,
            currency_code=data.get("currency_code", "KES"),
            category=category,
            date=tx_date,
            note=note,
            mpesa_ref=mpesa_ref,
            mpesa_raw_sms=raw_sms,
        )

        return Response({
            "id": transaction.id,
            "type": transaction.type,
            "amount": str(transaction.amount),
            "currency_code": transaction.currency_code,
            "category": transaction.category_id,
            "date": transaction.date.isoformat(),
            "note": transaction.note,
            "mpesa_ref": transaction.mpesa_ref,
        }, status=status.HTTP_201_CREATED)
