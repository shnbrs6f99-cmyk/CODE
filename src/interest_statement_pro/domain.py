from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum
from pathlib import Path


class VoucherType(StrEnum):
    OPENING = "Opening Balance"
    INVOICE = "Invoice"
    RECEIPT = "Receipt"
    DEBIT_NOTE = "Debit Note"
    CREDIT_NOTE = "Credit Note"
    JOURNAL = "Journal"
    CLOSING = "Closing Balance"
    UNKNOWN = "Unknown"


@dataclass(slots=True, frozen=True)
class LedgerTransaction:
    transaction_date: date
    voucher_type: VoucherType
    voucher_number: str
    narration: str
    debit: Decimal = Decimal(0)
    credit: Decimal = Decimal(0)
    source_page: int | None = None
    raw_text: str = ""

    @property
    def signed_amount(self) -> Decimal:
        return self.debit - self.credit


@dataclass(slots=True)
class LedgerStatement:
    customer_name: str
    period_start: date | None
    period_end: date | None
    opening_balance: Decimal
    closing_balance: Decimal
    transactions: list[LedgerTransaction]
    source_file: Path
    parser_name: str
    confidence: float = 1.0
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class InterestRules:
    annual_rate: Decimal = Decimal(18)
    credit_period_days: int = 30
    day_basis: int = 365
    grace_days: int = 0
    calculate_through: date | None = None
    charge_on_debit_notes: bool = True
    credit_notes_reduce_oldest: bool = True
    include_opening_balance: bool = True
    minimum_interest: Decimal = Decimal(0)
    round_places: int = 2


@dataclass(slots=True, frozen=True)
class Allocation:
    charge_voucher: str
    charge_date: date
    payment_voucher: str
    payment_date: date
    amount: Decimal


@dataclass(slots=True, frozen=True)
class InterestLine:
    voucher_number: str
    voucher_type: VoucherType
    transaction_date: date
    due_date: date
    settled_date: date
    principal: Decimal
    days_overdue: int
    annual_rate: Decimal
    interest: Decimal


@dataclass(slots=True)
class CalculationResult:
    statement: LedgerStatement
    allocations: list[Allocation]
    interest_lines: list[InterestLine]
    unallocated_credits: Decimal
    outstanding_principal: Decimal
    total_interest: Decimal
    validation_messages: list[str] = field(default_factory=list)
