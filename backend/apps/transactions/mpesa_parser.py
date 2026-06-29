import re
from datetime import date, datetime
from decimal import Decimal
from html import escape
from typing import Optional

PARSED_TX = dict


def parse_mpesa_sms(raw_sms: str) -> Optional[PARSED_TX]:
    cleaned = raw_sms.strip().replace("\n", " ").replace("\r", "")
    if not cleaned:
        return None

    amount = _extract_amount(cleaned)
    if amount is None:
        return None

    ref = _extract_ref(cleaned)
    counterparty = _extract_counterparty(cleaned)
    tx_type, tx_date = _classify(cleaned)

    return {
        "type": tx_type,
        "amount": str(amount),
        "currency_code": "KES",
        "date": tx_date.isoformat() if tx_date else date.today().isoformat(),
        "note": counterparty or "",
        "mpesa_ref": ref or "",
        "raw_sms": escape(raw_sms, quote=False),
    }


def _extract_amount(text: str) -> Optional[Decimal]:
    m = re.search(r"KSh\s*([\d,]+(?:\.\d{2})?)", text)
    if m:
        return Decimal(m.group(1).replace(",", ""))
    m = re.search(r"(?:sent|received|paid|withdrawn|airtime)\s+KSh\s*([\d,]+(?:\.\d{2})?)", text, re.IGNORECASE)
    if m:
        return Decimal(m.group(1).replace(",", ""))
    return None


def _extract_ref(text: str) -> Optional[str]:
    m = re.search(
        r"(?:Transaction code[,\s]*|transaction code[,\s]*|code[:\s]*|Code[:\s]*)([A-Z0-9]+)",
        text,
    )
    if m:
        return m.group(1)
    m = re.search(r"\b([A-Z]{2,4}\d{6,12}[A-Z0-9]?)\b", text)
    if m:
        return m.group(1)
    return None


def _extract_counterparty(text: str) -> Optional[str]:
    patterns = [
        r"(?:sent to|received from|paid to|withdrawn from|airtime to)\s+(.+?)\s+(?:on|til|bill|at)",
        r"(?:sent to|received from|paid to|withdrawn from|airtime to)\s+(.+?)(?:\s+(?:on|\d|$))",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            name = re.sub(r"\s+\d{9,12}$", "", name)
            name = re.sub(r"\s+(?:til|bill)\s*\.?\s*no\.?\s*\d+.*", "", name, flags=re.IGNORECASE)
            name = escape(name, quote=False)
            return name
    return None


def _extract_date(text: str) -> Optional[date]:
    patterns = [
        (r"on\s+(\d{1,2})/(\d{1,2})/(\d{2,4})", "%d/%m/%y"),
        (r"on\s+(\d{1,2})/(\d{1,2})/(\d{2,4})", "%m/%d/%y"),
        (r"on\s+(\d{4})-(\d{2})-(\d{2})", "%Y-%m-%d"),
        (r"on\s+(\d{1,2})-(\d{1,2})-(\d{2,4})", "%d-%m-%y"),
        (r"on\s+(\w+)\s+(\d{1,2}),?\s+(\d{4})", "%B %d %Y"),
        (r"on\s+(\d{1,2})\s+(\w+)\s+(\d{4})", "%d %B %Y"),
    ]
    for pat, fmt in patterns:
        m = re.search(pat, text)
        if m:
            try:
                parts = m.groups()
                if len(parts) == 3:
                    # For numeric date parts, try both DMY and MDY
                    if parts[0].isdigit() and parts[1].isdigit():
                        day, mon, yr = int(parts[0]), int(parts[1]), int(parts[2])
                        if yr < 100:
                            yr += 2000
                        if day > 12:
                            return date(yr, mon, day)
                        if mon > 12:
                            return date(yr, day, mon)
                        return date(yr, mon, day)
                    return datetime.strptime(m.group(0).replace("on ", ""), fmt).date()
            except (ValueError, OverflowError):
                continue
    return None


def _classify(text: str) -> tuple[str, Optional[date]]:
    tx_type = "expense"
    tx_date = _extract_date(text)

    low = text.lower()
    if re.search(r"\breceived\b", low):
        tx_type = "income"
    elif re.search(r"\bairtime\b", low):
        tx_type = "expense"
    elif re.search(r"\bwithdrawn\b", low):
        tx_type = "expense"
    elif re.search(r"\bsent\b", low):
        tx_type = "expense"
    elif re.search(r"\bpaid\b", low):
        tx_type = "expense"
    elif re.search(r"\bFuliza\b", text):
        tx_type = "expense"

    return tx_type, tx_date
