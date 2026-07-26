from datetime import date
from decimal import Decimal
from pathlib import Path

from interest_statement_pro.domain import LedgerStatement, LedgerTransaction, VoucherType
from interest_statement_pro.validation import LedgerValidator


def test_reconciliation_error_is_reported():
    statement = LedgerStatement(
        "Acme", date(2026, 1, 1), date(2026, 1, 31), Decimal(0), Decimal(900),
        [LedgerTransaction(date(2026, 1, 1), VoucherType.INVOICE, "I1", "", debit=Decimal(1000))],
        Path("x.pdf"), "test",
    )
    codes = {m.code for m in LedgerValidator().validate(statement)}
    assert "RECONCILIATION" in codes


def test_duplicate_detection():
    tx = LedgerTransaction(date(2026, 1, 1), VoucherType.INVOICE, "I1", "", debit=Decimal(100))
    statement = LedgerStatement("Acme", None, None, Decimal(0), Decimal(200), [tx, tx], Path("x.pdf"), "test")
    codes = {m.code for m in LedgerValidator().validate(statement)}
    assert "DUPLICATES" in codes
