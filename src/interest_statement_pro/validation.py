from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from .domain import LedgerStatement, VoucherType


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(slots=True, frozen=True)
class ValidationMessage:
    code: str
    severity: Severity
    message: str


class LedgerValidator:
    def validate(self, statement: LedgerStatement) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []
        if not statement.customer_name.strip():
            messages.append(ValidationMessage("CUSTOMER_MISSING", Severity.ERROR, "Customer name is missing"))
        if not statement.transactions:
            messages.append(ValidationMessage("NO_TRANSACTIONS", Severity.ERROR, "No transactions were extracted"))
        unknown = [t for t in statement.transactions if t.voucher_type == VoucherType.UNKNOWN]
        if unknown:
            messages.append(ValidationMessage("UNKNOWN_VOUCHERS", Severity.WARNING, f"{len(unknown)} voucher rows need review"))
        duplicates = set()
        seen = set()
        for tx in statement.transactions:
            key = (tx.transaction_date, tx.voucher_number, tx.debit, tx.credit)
            if key in seen:
                duplicates.add(key)
            seen.add(key)
            if tx.debit < 0 or tx.credit < 0:
                messages.append(ValidationMessage("NEGATIVE_COLUMN", Severity.ERROR, f"Negative debit/credit in {tx.voucher_number}"))
            if tx.debit and tx.credit:
                messages.append(ValidationMessage("BOTH_SIDES", Severity.WARNING, f"Both debit and credit populated in {tx.voucher_number}"))
        if duplicates:
            messages.append(ValidationMessage("DUPLICATES", Severity.WARNING, f"{len(duplicates)} duplicate transaction signatures found"))
        computed = statement.opening_balance + sum((t.signed_amount for t in statement.transactions), Decimal("0"))
        difference = (computed - statement.closing_balance).copy_abs()
        if difference > Decimal("0.05"):
            messages.append(ValidationMessage("RECONCILIATION", Severity.ERROR, f"Ledger does not reconcile; difference {difference}"))
        if statement.confidence < 0.7:
            messages.append(ValidationMessage("LOW_CONFIDENCE", Severity.WARNING, f"Parser confidence is {statement.confidence:.0%}"))
        return messages
