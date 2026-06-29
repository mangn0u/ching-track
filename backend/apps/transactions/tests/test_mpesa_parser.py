"""Unit tests for the M-Pesa SMS parser."""

from decimal import Decimal
from django.test import SimpleTestCase

from apps.transactions.mpesa_parser import (
    parse_mpesa_sms,
    _extract_amount,
    _extract_ref,
    _extract_counterparty,
    _classify,
)


class ExtractAmountTests(SimpleTestCase):
    def test_send_money(self):
        result = _extract_amount("KSh 1,500.00 sent to John")
        self.assertEqual(result, Decimal("1500.00"))

    def test_receive_money(self):
        result = _extract_amount("KSh 2,000.00 received from Jane")
        self.assertEqual(result, Decimal("2000.00"))

    def test_pay_bill(self):
        result = _extract_amount("KSh 3,000.00 paid to Kenya Power")
        self.assertEqual(result, Decimal("3000.00"))

    def test_buy_goods(self):
        result = _extract_amount("KSh 500.00 paid to SuperMart")
        self.assertEqual(result, Decimal("500.00"))

    def test_airtime(self):
        result = _extract_amount("KSh 100.00 airtime to 0722123456")
        self.assertEqual(result, Decimal("100.00"))

    def test_withdraw(self):
        result = _extract_amount("KSh 1,000.00 withdrawn from Agent")
        self.assertEqual(result, Decimal("1000.00"))

    def test_no_amount(self):
        result = _extract_amount("No money here")
        self.assertIsNone(result)

    def test_empty_string(self):
        result = _extract_amount("")
        self.assertIsNone(result)

    def test_integer_amount(self):
        result = _extract_amount("KSh 500 sent to John")
        self.assertEqual(result, Decimal("500"))


class ExtractRefTests(SimpleTestCase):
    def test_standard_ref(self):
        result = _extract_ref("Transaction code, RKX123456Z.")
        self.assertEqual(result, "RKX123456Z")

    def test_code_prefix(self):
        result = _extract_ref("Code: ABC789DEF")
        self.assertEqual(result, "ABC789DEF")

    def test_no_ref(self):
        result = _extract_ref("No code here")
        self.assertIsNone(result)


class ExtractCounterpartyTests(SimpleTestCase):
    def test_send_money(self):
        result = _extract_counterparty("sent to John Doe 0722123456 on 29/6/26")
        self.assertEqual(result, "John Doe")

    def test_receive_money(self):
        result = _extract_counterparty("received from Jane Smith 0711123456 on 29/6/26")
        self.assertEqual(result, "Jane Smith")

    def test_pay_bill(self):
        result = _extract_counterparty("paid to Kenya Power bill no. 123456 on 29/6/26")
        self.assertEqual(result, "Kenya Power")

    def test_buy_goods(self):
        result = _extract_counterparty("paid to SuperMart till no. 123456 on 29/6/26")
        self.assertEqual(result, "SuperMart")

    def test_withdraw(self):
        result = _extract_counterparty("withdrawn from JAMES KAMAU on 29/6/26")
        self.assertEqual(result, "JAMES KAMAU")

    def test_xss_sanitized(self):
        result = _extract_counterparty('sent to <script>alert(1)</script> 0722000000 on 29/6/26')
        self.assertEqual(result, "&lt;script&gt;alert(1)&lt;/script&gt;")

    def test_no_counterparty(self):
        result = _extract_counterparty("Some random text")
        self.assertIsNone(result)


class ClassifyTests(SimpleTestCase):
    def test_receive_is_income(self):
        result, _ = _classify("KSh 500 received from Jane")
        self.assertEqual(result, "income")

    def test_send_is_expense(self):
        result, _ = _classify("KSh 500 sent to John")
        self.assertEqual(result, "expense")

    def test_paid_is_expense(self):
        result, _ = _classify("KSh 500 paid to Store")
        self.assertEqual(result, "expense")

    def test_withdrawn_is_expense(self):
        result, _ = _classify("KSh 500 withdrawn from ATM")
        self.assertEqual(result, "expense")

    def test_airtime_is_expense(self):
        result, _ = _classify("KSh 100 airtime to 0722")
        self.assertEqual(result, "expense")


class FullParseTests(SimpleTestCase):
    def test_send_money_sms(self):
        sms = "KSh 1,500.00 sent to John Doe 0722123456 on 29/6/26 at 10:30 AM. New M-PESA balance is KSh 5,000.00. Transaction code, RKX123456Z."
        result = parse_mpesa_sms(sms)
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "expense")
        self.assertEqual(result["amount"], "1500.00")
        self.assertEqual(result["currency_code"], "KES")
        self.assertEqual(result["note"], "John Doe")
        self.assertEqual(result["mpesa_ref"], "RKX123456Z")

    def test_receive_money_sms(self):
        sms = "KSh 2,000.00 received from Jane Smith 0711123456 on 15/6/26 at 2:45 PM. New M-PESA balance is KSh 12,000.00. Transaction code, RKX789012Z."
        result = parse_mpesa_sms(sms)
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "income")
        self.assertEqual(result["amount"], "2000.00")
        self.assertEqual(result["note"], "Jane Smith")

    def test_buy_goods_sms(self):
        sms = "KSh 500.00 paid to SuperMart till no. 123456 on 29/6/26 at 11:15 AM. New M-PESA balance is KSh 4,500.00. Transaction code, RKX345678Z."
        result = parse_mpesa_sms(sms)
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "expense")
        self.assertEqual(result["amount"], "500.00")
        self.assertEqual(result["note"], "SuperMart")

    def test_pay_bill_sms(self):
        sms = "KSh 3,000.00 paid to Kenya Power bill no. 1234567890 on 29/6/26 at 9:00 AM. New M-PESA balance is KSh 7,000.00. Transaction code, RKX901234Z."
        result = parse_mpesa_sms(sms)
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "expense")
        self.assertEqual(result["amount"], "3000.00")
        self.assertEqual(result["note"], "Kenya Power")

    def test_withdraw_sms(self):
        sms = "KSh 1,000.00 withdrawn from JAMES KAMAU on 29/6/26 at 8:30 AM. New M-PESA balance is KSh 6,000.00. Transaction code, RKX567890Z."
        result = parse_mpesa_sms(sms)
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "expense")
        self.assertEqual(result["amount"], "1000.00")
        self.assertEqual(result["note"], "JAMES KAMAU")

    def test_airtime_sms(self):
        sms = "KSh 100.00 airtime to 0722123456 on 29/6/26 at 7:00 AM. New M-PESA balance is KSh 6,100.00. Transaction code, RKX123789Z."
        result = parse_mpesa_sms(sms)
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "expense")
        self.assertEqual(result["amount"], "100.00")
        self.assertEqual(result["note"], "0722123456")

    def test_invalid_sms_returns_none(self):
        result = parse_mpesa_sms("Hello, this is not an M-Pesa message.")
        self.assertIsNone(result)

    def test_empty_sms_returns_none(self):
        result = parse_mpesa_sms("")
        self.assertIsNone(result)

    def test_whitespace_sms_returns_none(self):
        result = parse_mpesa_sms("   ")
        self.assertIsNone(result)

    def test_xss_in_sms_is_sanitized(self):
        sms = 'KSh 500.00 sent to <script>alert(1)</script> 0722000000 on 29/6/26 at 10:30 AM. Transaction code, XSS123.'
        result = parse_mpesa_sms(sms)
        self.assertIsNotNone(result)
        self.assertNotIn("<script>", result["note"])
        self.assertIn("&lt;script&gt;", result["note"])
        self.assertNotIn("<script>", result["raw_sms"])
        self.assertIn("&lt;script&gt;", result["raw_sms"])
