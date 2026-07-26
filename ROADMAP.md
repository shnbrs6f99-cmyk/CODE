# Interest Statement Generator Pro — Master Development Roadmap

This roadmap mirrors GitHub issue **Master Development Roadmap** and is maintained as implementation progresses.

## Status legend
- [ ] Planned
- [x] Completed and validated

## Foundation
- [x] Repository initialized
- [ ] Python 3.12 project configuration finalized
- [ ] Clean architecture package structure
- [ ] Central configuration and application paths
- [ ] Logging and crash reporting
- [ ] Domain exceptions and validation framework

## Domain and Calculation Engine
- [ ] Ledger, transaction, allocation, customer, settings, and result models
- [ ] Voucher type normalization
- [ ] FIFO receipt/payment allocation
- [ ] Credit-period calculation
- [ ] Configurable interest rules
- [ ] Debit note and credit note treatment
- [ ] Opening and closing balance reconciliation
- [ ] Rounding and financial precision policy
- [ ] Validation and audit trail

## PDF Ingestion and Parsing
- [ ] Safe PDF loading and metadata inspection
- [ ] Text extraction fallback pipeline
- [ ] Multiple Tally Prime layout detection
- [ ] Parser strategy registry
- [ ] Opening balance extraction
- [ ] Invoice extraction
- [ ] Receipt extraction
- [ ] Debit/credit note extraction
- [ ] Closing balance extraction
- [ ] Multi-page row reconstruction
- [ ] Malformed/encrypted/scanned PDF handling
- [ ] Parser confidence scoring and warnings
- [ ] Extensible layout fixtures and regression tests

## Persistence
- [ ] SQLite schema and migrations
- [ ] Customer database
- [ ] Customer-specific interest defaults
- [ ] Application settings and saved preferences
- [ ] Processing history
- [ ] Generated report history
- [ ] Database backup and integrity checks

## Processing Services
- [ ] Single-file workflow
- [ ] Batch processing workflow
- [ ] Bounded worker pool for hundreds of PDFs
- [ ] Cancellation and progress reporting
- [ ] Duplicate-file detection
- [ ] Safe output naming and collision handling
- [ ] Per-file success/failure isolation
- [ ] Batch summary reporting

## Excel Reporting
- [ ] Accountant-grade workbook structure
- [ ] Statement summary sheet
- [ ] Transaction and FIFO allocation sheet
- [ ] Interest calculation sheet
- [ ] Exceptions and validation sheet
- [ ] Professional typography, borders, number formats, freezes, filters, print setup
- [ ] Customer/company branding fields
- [ ] Formula and total verification
- [ ] Workbook metadata and audit information

## Windows Desktop UI
- [ ] Modern CustomTkinter application shell
- [ ] Dashboard
- [ ] PDF selection and drag/drop-friendly workflow
- [ ] Batch queue and progress view
- [ ] Customer management
- [ ] Interest settings editor
- [ ] Parsing preview and correction workflow
- [ ] Validation/error center
- [ ] Processing history
- [ ] Saved preferences and theme
- [ ] Responsive background processing
- [ ] Accessibility and keyboard navigation

## Quality and Operations
- [ ] Unit tests for calculation engine
- [ ] Parser fixture tests
- [ ] Database integration tests
- [ ] Excel generation tests
- [ ] Batch processing tests
- [ ] UI smoke tests where practical
- [ ] Ruff and mypy checks
- [ ] GitHub Actions CI
- [ ] Structured application logs
- [ ] Diagnostic bundle export

## Packaging and Distribution
- [ ] PyInstaller spec
- [ ] Windows executable build script
- [ ] Version metadata and icon hooks
- [ ] Data-file collection validation
- [ ] Clean-machine installation verification guide
- [ ] Release checklist

## Documentation
- [ ] README
- [ ] Installation guide
- [ ] User manual
- [ ] Developer guide
- [ ] Architecture decision records
- [ ] Troubleshooting guide
- [ ] Sample workflow and privacy notes

## Commercial Readiness Gate
- [ ] Complete feature coverage
- [ ] All automated tests passing
- [ ] Representative Tally PDF layouts validated
- [ ] Malformed input scenarios verified
- [ ] Large batch stress test completed
- [ ] Excel output manually reviewed for accountant use
- [ ] Windows executable build verified
- [ ] Documentation complete
- [ ] No known critical or high-severity defects

## Maintenance instruction
Codex must update this roadmap and the corresponding GitHub issue after each meaningful module is completed. A checkbox may only be marked complete after implementation, relevant tests, and documentation are committed. Each update should include commit or PR references and list any newly discovered work.