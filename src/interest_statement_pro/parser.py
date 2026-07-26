from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import ClassVar

import pdfplumber
from pdfplumber.utils.exceptions import PdfminerException
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from .domain import LedgerStatement, LedgerTransaction, VoucherType

DATE_RE = re.compile(r"^(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})\s+")
MONEY_RE = re.compile(r"(?P<amount>[\d,]+(?:\.\d{1,2})?)\s*(?P<side>Dr|Cr)?$", re.IGNORECASE)


class PdfParseError(RuntimeError):
    pass


@dataclass(slots=True)
class ExtractedPdf:
    pages: list[str]
    encrypted: bool = False


class PdfTextExtractor:
    def extract(self, path: Path) -> ExtractedPdf:
        if not path.exists() or path.suffix.lower() != ".pdf":
            raise PdfParseError(f"Not a readable PDF: {path}")
        try:
            reader = PdfReader(str(path))
            if reader.is_encrypted and reader.decrypt("") == 0:
                raise PdfParseError("Password-protected PDF is not supported without a password")
            pages = [(page.extract_text() or "") for page in reader.pages]
            if sum(len(p.strip()) for p in pages) >= 80:
                return ExtractedPdf(pages=pages, encrypted=reader.is_encrypted)
        except PdfParseError:
            raise
        except (OSError, ValueError, TypeError, RuntimeError, PyPdfError):
            pages = []

        try:
            with pdfplumber.open(path) as pdf:
                pages = [
                    page.extract_text(x_tolerance=2, y_tolerance=3) or ""
                    for page in pdf.pages
                ]
        except (OSError, ValueError, TypeError, RuntimeError, PdfminerException) as exc:
            raise PdfParseError(f"Unable to read PDF: {exc}") from exc
        if sum(len(p.strip()) for p in pages) < 20:
            raise PdfParseError("PDF contains no usable text; it may be scanned or malformed")
        return ExtractedPdf(pages=pages)


class TallyLedgerParser:
    """Heuristic parser supporting common Tally Prime ledger PDF variants."""

    VOUCHER_ALIASES: ClassVar[dict[str, VoucherType]] = {
        "sales": VoucherType.INVOICE,
        "invoice": VoucherType.INVOICE,
        "receipt": VoucherType.RECEIPT,
        "payment": VoucherType.RECEIPT,
        "debit note": VoucherType.DEBIT_NOTE,
        "credit note": VoucherType.CREDIT_NOTE,
        "journal": VoucherType.JOURNAL,
    }

    def __init__(self, extractor: PdfTextExtractor | None = None) -> None:
        self.extractor = extractor or PdfTextExtractor()

    def parse(self, path: Path) -> LedgerStatement:
        extracted = self.extractor.extract(path)
        full_text = "\n".join(extracted.pages)
        customer = self._customer_name(full_text, path)
        opening = self._named_balance(full_text, "opening balance")
        closing = self._named_balance(full_text, "closing balance")
        transactions: list[LedgerTransaction] = []
        warnings: list[str] = []

        for page_no, page in enumerate(extracted.pages, start=1):
            for raw in page.splitlines():
                tx = self._parse_line(raw, page_no)
                if tx:
                    transactions.append(tx)

        if not transactions:
            warnings.append("No transaction rows were recognized; verify the PDF layout")
        dates = [t.transaction_date for t in transactions]
        computed = opening + sum((t.signed_amount for t in transactions), Decimal(0))
        if closing == Decimal(0) and computed != 0:
            closing = computed
            warnings.append("Closing balance inferred from opening balance and transactions")
        confidence = min(1.0, 0.35 + (0.5 if transactions else 0) + (0.15 if customer else 0))
        return LedgerStatement(
            customer_name=customer,
            period_start=min(dates) if dates else None,
            period_end=max(dates) if dates else None,
            opening_balance=opening,
            closing_balance=closing,
            transactions=transactions,
            source_file=path,
            parser_name="TallyHeuristicParser-v1",
            confidence=confidence,
            warnings=warnings,
        )

    def _parse_line(self, raw: str, page_no: int) -> LedgerTransaction | None:
        line = " ".join(raw.split())
        match = DATE_RE.match(line)
        if not match:
            return None
        tx_date = self._date(match.group(1))
        if not tx_date:
            return None
        tail = line[match.end():]
        voucher_type = self._voucher_type(tail)
        money = MONEY_RE.search(tail)
        if not money:
            return None
        amount = self._decimal(money.group("amount"))
        side = (money.group("side") or "").lower()
        prefix = tail[: money.start()].strip()
        tokens = prefix.split()
        voucher_number = next((t for t in reversed(tokens) if any(c.isdigit() for c in t)), "")
        debit = (
            amount
            if side == "dr" or voucher_type in {VoucherType.INVOICE, VoucherType.DEBIT_NOTE}
            else Decimal(0)
        )
        credit = (
            amount
            if side == "cr" or voucher_type in {VoucherType.RECEIPT, VoucherType.CREDIT_NOTE}
            else Decimal(0)
        )
        if debit == 0 and credit == 0:
            debit = amount
        return LedgerTransaction(
            transaction_date=tx_date,
            voucher_type=voucher_type,
            voucher_number=voucher_number or f"PAGE{page_no}",
            narration=prefix,
            debit=debit,
            credit=credit,
            source_page=page_no,
            raw_text=raw,
        )

    def _voucher_type(self, text: str) -> VoucherType:
        lowered = text.lower()
        for alias, kind in self.VOUCHER_ALIASES.items():
            if alias in lowered:
                return kind
        return VoucherType.UNKNOWN

    @staticmethod
    def _date(value: str) -> date | None:
        normalized = value.replace("/", "-").replace(".", "-")
        parts = normalized.split("-")
        if len(parts) != 3:
            return None
        try:
            day, month, year = (int(part) for part in parts)
            if year < 100:
                year += 2000
            return date(year, month, day)
        except ValueError:
            return None

    @staticmethod
    def _decimal(value: str) -> Decimal:
        try:
            return Decimal(value.replace(",", ""))
        except InvalidOperation:
            return Decimal(0)

    def _named_balance(self, text: str, label: str) -> Decimal:
        pattern = re.compile(
            re.escape(label) + r"[^\d]*(\d[\d,]*(?:\.\d{1,2})?)\s*(Dr|Cr)?",
            re.IGNORECASE,
        )
        match = pattern.search(text)
        if not match:
            return Decimal(0)
        amount = self._decimal(match.group(1))
        return -amount if (match.group(2) or "").lower() == "cr" else amount

    @staticmethod
    def _customer_name(text: str, path: Path) -> str:
        patterns = [
            r"Ledger Account\s*\n\s*([^\n]+)",
            r"Ledger:\s*([^\n]+)",
            r"Account:\s*([^\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip(" :-")
        return path.stem
