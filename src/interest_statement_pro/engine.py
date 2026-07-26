from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from .domain import (
    Allocation,
    CalculationResult,
    InterestLine,
    InterestRules,
    LedgerStatement,
    LedgerTransaction,
    VoucherType,
)


@dataclass(slots=True)
class _OpenCharge:
    transaction: LedgerTransaction
    remaining: Decimal


def _money(value: Decimal, places: int) -> Decimal:
    quantum = Decimal(1).scaleb(-places)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


class InterestCalculator:
    """Deterministic FIFO allocator and simple-interest calculator."""

    def calculate(self, statement: LedgerStatement, rules: InterestRules) -> CalculationResult:
        cutoff = rules.calculate_through or statement.period_end or date.today()
        charges: deque[_OpenCharge] = deque()
        allocations: list[Allocation] = []
        interest_lines: list[InterestLine] = []
        unallocated_credits = Decimal(0)

        if rules.include_opening_balance and statement.opening_balance > 0:
            opening_date = statement.period_start or min(
                (t.transaction_date for t in statement.transactions), default=cutoff
            )
            charges.append(
                _OpenCharge(
                    LedgerTransaction(
                        transaction_date=opening_date,
                        voucher_type=VoucherType.OPENING,
                        voucher_number="OPENING",
                        narration="Opening balance",
                        debit=statement.opening_balance,
                    ),
                    statement.opening_balance,
                )
            )

        ordered = sorted(statement.transactions, key=lambda t: (t.transaction_date, t.voucher_number))
        for tx in ordered:
            amount = tx.signed_amount
            is_charge = tx.voucher_type in {
                VoucherType.INVOICE,
                VoucherType.DEBIT_NOTE,
                VoucherType.JOURNAL,
            } and amount > 0
            if tx.voucher_type == VoucherType.DEBIT_NOTE and not rules.charge_on_debit_notes:
                is_charge = False
            if is_charge:
                charges.append(_OpenCharge(tx, amount))
                continue

            credit = -amount if amount < 0 else Decimal(0)
            if credit <= 0:
                continue
            while credit > 0 and charges:
                charge = charges[0]
                applied = min(credit, charge.remaining)
                allocations.append(
                    Allocation(
                        charge_voucher=charge.transaction.voucher_number,
                        charge_date=charge.transaction.transaction_date,
                        payment_voucher=tx.voucher_number,
                        payment_date=tx.transaction_date,
                        amount=applied,
                    )
                )
                self._append_interest(
                    interest_lines,
                    charge.transaction,
                    applied,
                    tx.transaction_date,
                    rules,
                )
                charge.remaining -= applied
                credit -= applied
                if charge.remaining == 0:
                    charges.popleft()
            unallocated_credits += credit

        outstanding = Decimal(0)
        for charge in charges:
            outstanding += charge.remaining
            self._append_interest(
                interest_lines,
                charge.transaction,
                charge.remaining,
                cutoff,
                rules,
            )

        total = _money(sum((line.interest for line in interest_lines), Decimal(0)), rules.round_places)
        if Decimal(0) < total < rules.minimum_interest:
            total = rules.minimum_interest
        return CalculationResult(
            statement=statement,
            allocations=allocations,
            interest_lines=interest_lines,
            unallocated_credits=_money(unallocated_credits, rules.round_places),
            outstanding_principal=_money(outstanding, rules.round_places),
            total_interest=total,
        )

    def _append_interest(
        self,
        target: list[InterestLine],
        charge: LedgerTransaction,
        principal: Decimal,
        settled_date: date,
        rules: InterestRules,
    ) -> None:
        due = charge.transaction_date + timedelta(
            days=rules.credit_period_days + rules.grace_days
        )
        days = max(0, (settled_date - due).days)
        interest = principal * rules.annual_rate * Decimal(days) / (
            Decimal(100) * Decimal(rules.day_basis)
        )
        target.append(
            InterestLine(
                voucher_number=charge.voucher_number,
                voucher_type=charge.voucher_type,
                transaction_date=charge.transaction_date,
                due_date=due,
                settled_date=settled_date,
                principal=_money(principal, rules.round_places),
                days_overdue=days,
                annual_rate=rules.annual_rate,
                interest=_money(interest, rules.round_places),
            )
        )
