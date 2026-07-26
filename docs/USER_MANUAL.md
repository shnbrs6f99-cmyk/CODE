# User Manual

## Supported input

Use ledger account PDFs exported directly from Tally Prime. Text-based PDFs work best. Scanned image-only PDFs are rejected with a clear message because OCR is not included in the commercial core.

## Processing a batch

1. Click **Add PDF Files** or **Add Folder**.
2. Confirm the queue contains the intended ledgers.
3. Set annual rate, credit period, and worker count.
4. Click **Generate Statements**.
5. Select an output directory.
6. Wait for the completion summary. A failed file does not stop the rest of the batch.

## Workbook sheets

- **Summary:** customer, period, settings, balances, outstanding principal, and total interest.
- **Transactions:** extracted ledger rows with source page numbers.
- **FIFO Allocations:** payment-to-charge allocation audit trail.
- **Interest Calculation:** due dates, settlement dates, overdue days, principal portions, rates, and interest.
- **Validation:** reconciliation errors, low-confidence parsing, duplicate signatures, and unknown voucher types.

## Reviewing results

Always review the Validation sheet before issuing an interest statement. Correct the source PDF or use a supported Tally export layout when the workbook reports missing transactions, unknown vouchers, low confidence, or a reconciliation error.

## Stored data

The application saves customer names, default commercial settings, the previous output location, and processing history in a local SQLite database. It does not upload ledgers or customer data.

## Backup

Back up the application-data folder regularly. The database uses SQLite WAL mode and performs an integrity check through the developer API.
