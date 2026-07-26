# Troubleshooting

## No transactions recognized

The PDF may be scanned, password-protected, customized, or use an unsupported column order. Export the ledger again from Tally Prime as a text-based PDF and inspect the Validation sheet. Preserve a sanitized sample for a parser regression test.

## Ledger does not reconcile

Compare opening balance plus extracted debits minus extracted credits against the closing balance. Common causes are repeated page headers interpreted as rows, wrapped narrations, omitted rows, or Dr/Cr markers positioned differently.

## Excel file cannot be saved

Close an existing workbook with the same filename and confirm write permission for the destination folder. The application generates a numbered filename when a target already exists.

## Application does not start

For source installs, confirm Python 3.12 and reinstall dependencies. For packaged builds, inspect the rotating log at the platform user log directory.

## Batch is slow

Use four workers on typical office hardware. Increasing beyond eight is blocked intentionally to avoid excessive memory and disk contention. Large or image-heavy PDFs take longer to extract.

## Diagnostic information

Logs include timestamps, severity, module name, source path, and stack traces. Do not publicly share logs without reviewing customer names and file paths.
