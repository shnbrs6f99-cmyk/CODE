# Interest Statement Generator Pro — Master Development Roadmap

This roadmap mirrors GitHub issue **#1 — Master Development Roadmap**.

## Current release stage

**v0.9.0-beta — real-user validation. Not production-certified.**

The implementation baseline is complete enough for controlled beta testing. Commercial production readiness remains blocked on representative Tally PDF validation, accounting review, stress testing, signed distribution, and clean-machine verification.

## Implemented baseline

- [x] Python 3.12 project and dependency configuration
- [x] Modular domain, parser, calculation, reporting, storage, service, and UI layers
- [x] Tally PDF text extraction fallback pipeline
- [x] Heuristic ledger transaction and balance extraction
- [x] FIFO receipt allocation and configurable interest calculation
- [x] Excel workbook generation with audit and validation sheets
- [x] SQLite customer, preference, and processing-history storage
- [x] Bounded parallel batch processing and per-file failure isolation
- [x] CustomTkinter Windows desktop application
- [x] Structured logging and exception handling
- [x] Parser diagnostic ZIP export for failed/unsupported PDFs
- [x] Automated domain, database, Excel, and diagnostic tests
- [x] GitHub Actions Windows validation pipeline
- [x] PyInstaller Windows build configuration
- [x] README, user, developer, troubleshooting, and beta testing guides
- [x] Sample input and sample output folders

## v0.9.0-beta release validation

The Windows workflow must complete all items below before the beta release is considered technically published:

- [ ] Ruff passes on Windows runner
- [ ] Mypy passes on Windows runner
- [ ] Complete pytest suite passes on Python 3.12 Windows runner
- [ ] PyInstaller build completes on `windows-latest`
- [ ] Built executable exists and passes size/smoke validation
- [ ] ZIP build artifact and SHA-256 file are uploaded
- [ ] GitHub pre-release `v0.9.0-beta` is created and artifact attached

## Exact remaining real-user validation tasks

### Parser coverage

- [ ] Collect sanitized fixtures for each materially different Tally Prime ledger PDF layout encountered
- [ ] Validate at least 25 customer ledgers across multiple Tally Prime versions and export configurations
- [ ] Include single-page, multi-page, wide-column, wrapped narration, and page-break transaction cases
- [ ] Include debit-balance and credit-balance opening/closing cases
- [ ] Include sales invoices, receipts, debit notes, credit notes, journals, and mixed voucher ledgers
- [ ] Confirm no transaction is dropped, duplicated, merged incorrectly, or assigned the wrong debit/credit direction
- [ ] Add a regression fixture and automated test for every confirmed parser defect
- [ ] Determine whether OCR support is required for scanned Tally exports; current beta reports these as unsupported

### Accounting and calculation review

- [ ] Obtain written accountant approval for FIFO allocation behavior
- [ ] Confirm treatment of opening debit and credit balances
- [ ] Confirm treatment of advances/unallocated receipts
- [ ] Confirm debit-note and credit-note allocation rules
- [ ] Confirm whether interest is charged through payment date, day before payment, or another convention
- [ ] Confirm 365/366/fixed-year basis requirements
- [ ] Confirm rounding level and timing against accountant calculations
- [ ] Compare at least 20 generated statements with independently calculated expected results

### Excel and usability review

- [ ] Manually inspect generated workbooks in supported Microsoft Excel versions
- [ ] Verify totals, print areas, page orientation, freeze panes, filters, and number/date formats
- [ ] Confirm accountant terminology and workbook sheet naming
- [ ] Validate customer-name sanitization and output collision handling
- [ ] Conduct keyboard and high-DPI Windows usability testing
- [ ] Validate error messages with non-technical users

### Reliability and scale

- [ ] Process a batch of at least 100 representative PDFs without application termination
- [ ] Process a batch of at least 500 PDFs for memory, duration, cancellation, and database-write behavior
- [ ] Test malformed, truncated, encrypted, empty-text, and renamed non-PDF files
- [ ] Verify parser diagnostic packages for every failure class
- [ ] Test duplicate inputs and repeated processing into the same output folder
- [ ] Perform SQLite integrity, backup, migration, and interrupted-write tests

### Windows distribution

- [ ] Test the beta artifact on clean Windows 10 and Windows 11 machines without Python installed
- [ ] Verify startup, PDF selection, processing, Excel output, database persistence, and diagnostics on clean machines
- [ ] Add a production icon and Windows version metadata
- [ ] Code-sign the executable with an organization certificate before commercial distribution
- [ ] Decide installer format and implement upgrade/uninstall behavior
- [ ] Run antivirus and SmartScreen reputation validation

### Security, privacy, and commercial controls

- [ ] Complete a privacy review for ledger data, logs, diagnostics, and database retention
- [ ] Add an in-app diagnostic privacy warning and explicit consent before including original PDFs
- [ ] Define data backup, export, and deletion procedures
- [ ] Perform dependency vulnerability scanning and license review
- [ ] Complete legal review of disclaimers and commercial terms

## Production readiness gate

Do not call the application production-ready until every applicable validation item above is completed, all critical/high defects are closed, the executable is code-signed, and an accountant has approved the calculation conventions.

## Maintenance instruction

Codex must update this roadmap and Issue #1 after each validation milestone. Every completed checkbox must reference the confirming workflow run, commit, test evidence, or signed review record.
