# Interest Statement Generator Pro

Commercial Windows desktop software for reading Tally Prime ledger PDFs, allocating receipts FIFO, calculating overdue interest, and generating accountant-grade Excel statements.

## Features

- Multiple-layout heuristic Tally Prime PDF parser with extraction fallbacks
- Opening balance, invoices, receipts, debit notes, credit notes, and closing balance handling
- FIFO allocation with configurable annual rate, credit period, grace period, day basis, cut-off date, and rounding
- Reconciliation and validation warnings
- Professional multi-sheet Excel workbooks
- Batch processing with bounded parallel workers and per-file failure isolation
- SQLite customer, preference, and processing-history database
- Rotating logs and global crash logging
- Modern CustomTkinter desktop interface
- PyInstaller Windows executable configuration

## Requirements

- Windows 10 or Windows 11
- Python 3.12 or newer for source installation

## Installation from source

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
interest-statement-pro
```

## Usage

1. Select one or more Tally Prime ledger PDFs, or select a folder.
2. Enter the annual interest rate and credit period.
3. Choose the number of workers. Four is a safe default.
4. Click **Generate Statements** and select an output folder.
5. Review the generated workbook's Summary, Transactions, FIFO Allocations, Interest Calculation, and Validation sheets.

## Accounting behaviour

- Debits from invoices, debit notes, and journals become FIFO charges.
- Receipts and credit notes reduce the oldest charge first.
- Interest begins after the configured credit period and grace period.
- Simple interest uses `principal × annual rate × overdue days / day basis`.
- Monetary results use `Decimal` and round half-up to two decimal places by default.
- The application reports reconciliation differences rather than silently changing source figures.

## Data and privacy

PDFs are processed locally. Customer data, preferences, and processing history are stored in the user's local application-data directory. Logs contain file paths and error diagnostics but not PDF binary content.

## Testing

```powershell
pytest
ruff check src tests
mypy src
```

## Windows executable

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

The executable is created under `dist/InterestStatementGeneratorPro/`.

## Documentation

- [User Manual](docs/USER_MANUAL.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Master Roadmap](ROADMAP.md)

## Important limitation

Tally PDF exports are not a formal machine-readable interchange format. The parser uses layered heuristics and confidence warnings. New or customized layouts should be added as regression fixtures before commercial deployment to those customers.
