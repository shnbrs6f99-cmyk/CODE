from datetime import date
from decimal import Decimal
from pathlib import Path

from interest_statement_pro.domain import InterestRules, LedgerStatement, LedgerTransaction, VoucherType
from interest_statement_pro.engine import InterestCalculator


def test_fifo_allocation_and_interest():
    statement = LedgerStatement(
        customer_name="Acme",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
        opening_balance=Decimal("0"),
        closing_balance=Decimal("500"),
        source_file=Path("ledger.pdf"),
        parser_name="test",
        transactions=[
            LedgerTransaction(date(2026, 1, 1), VoucherType.INVOICE, "INV-1", "", Decimal("1000")),
            LedgerTransaction(date(2026, 1, 15), VoucherType.INVOICE, "INV-2", "", Decimal("500")),
            LedgerTransaction(date(2026, 2, 15), VoucherType.RECEIPT, "RCPT-1", "", credit=Decimal("1000")),
        ],
    )
    result = InterestCalculator().calculate(
        statement,
        InterestRules(annual_rate=Decimal("18"), credit_period_days=30, calculate_through=date(2026, 3, 31)),
    )
    assert result.allocations[0].charge_voucher == "INV-1"
    assert result.allocations[0].amount == Decimal("1000")
    assert result.outstanding_principal == Decimal("500.00")
    assert result.total_interest == Decimal("11.10")


def test_unallocated_credit_is_preserved():
    statement = LedgerStatement("Acme", None, date(2026, 1, 31), Decimal("0"), Decimal("-25"), [
        LedgerTransaction(date(2026, 1, 1), VoucherType.RECEIPT, "R1", "", credit=Decimal("25"))
    ], Path("x.pdf"), "test")
    result = InterestCalculator().calculate(statement, InterestRules())
    assert result.unallocated_credits == Decimal("25.00")
    assert result.total_interest == Decimal("0.00")
