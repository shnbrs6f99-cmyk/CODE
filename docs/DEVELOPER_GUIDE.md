# Developer Guide

## Architecture

The application follows a layered architecture:

- `domain.py`: immutable financial entities and calculation contracts.
- `engine.py`: deterministic FIFO and interest policy implementation.
- `parser.py`: PDF extraction fallback and Tally-specific parsing heuristics.
- `validation.py`: independent reconciliation and data-quality rules.
- `reporting.py`: Excel presentation adapter.
- `storage.py`: SQLite repository and preferences adapter.
- `services.py`: application orchestration and batch concurrency.
- `gui.py`: desktop presentation layer.
- `app.py`: composition root.

Dependencies point inward: domain and financial rules do not depend on the UI, database, or PDF libraries.

## Adding a Tally layout

1. Add a sanitized representative PDF fixture or extracted-text fixture under `tests/fixtures/`.
2. Write a regression test for customer name, balances, row count, voucher types, and reconciliation.
3. Add a focused parser strategy or extend aliases without weakening existing recognition.
4. Record parser warnings when inference is required.
5. Never silently fabricate dates, amounts, voucher numbers, or balances.

## Financial precision

All monetary calculations use `Decimal`. Inputs should be constructed from strings. The default policy uses simple interest, 365-day basis, and round-half-up at output boundaries.

## Database

SQLite is initialized automatically under the platform-specific user data folder. Schema changes must be forward-only and versioned through `schema_version`. Long-running reads and writes should remain short because batch workers share the database file.

## Error policy

Input-specific errors are returned as failed `ProcessingOutcome` objects. Programming faults are logged with tracebacks. A batch must continue when one source file fails.

## Release process

1. Update version in `pyproject.toml` and `__init__.py`.
2. Run `pytest`, `ruff check src tests`, and `mypy src`.
3. Build on Windows with `scripts/build_windows.ps1`.
4. Test on a clean Windows 10/11 machine.
5. Validate representative Tally layouts and a large batch.
6. Update the Master Development Roadmap issue and release notes.
