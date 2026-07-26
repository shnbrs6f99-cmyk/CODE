# Interest Statement Generator Pro — Beta Testing Guide

> Version: v0.9.0-beta  
> Status: Real-user validation build. This is **not yet a production-certified release**.

## 1. Launch the application

### Using the Windows build artifact

1. Download `InterestStatementGeneratorPro-v0.9.0-beta-win64.zip` from the GitHub pre-release.
2. Verify its SHA-256 value against `InterestStatementGeneratorPro-v0.9.0-beta-win64.sha256.txt`.
3. Extract the complete ZIP into a writable folder such as `Documents\Interest Statement Generator Pro`.
4. Do not move only the `.exe`; the adjacent runtime files in the extracted folder are required.
5. Double-click `InterestStatementGeneratorPro.exe` inside the extracted folder.
6. If Windows SmartScreen appears, choose **More info** and then **Run anyway** only after confirming the file came from the official repository release.
7. The application creates its local database, preferences, and logs under the current Windows user's application-data folder.

### Running from source

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m interest_statement_pro.app
```

## 2. Import a Tally ledger PDF

1. Export the required customer ledger from Tally Prime as a text-based PDF.
2. Open the application.
3. Choose **Add PDFs** and select one or more ledger PDF files.
4. Choose an output folder. For repository-based testing, `sample_output` may be used.
5. Enter the annual interest rate and credit period.
6. Start processing.
7. Watch the status of each file in the batch queue.

For initial validation, process one PDF at a time and manually compare the opening balance, every voucher, receipts, debit/credit notes, FIFO allocation, due dates, closing balance, and total interest with the source ledger.

## 3. Find the Excel output

The workbook is saved in the output folder selected in the application. The filename is similar to:

`Customer_Name_Interest_Statement.xlsx`

If a file with that name already exists, the application adds a sequence number rather than overwriting it.

The workbook contains the statement summary, parsed transactions, FIFO allocations, interest calculations, and validation messages.

## 4. Report parser errors

When processing fails, the application automatically creates:

`<Selected Output Folder>\Parser Diagnostics\<PDF_Name>_Parser_Diagnostics.zip`

The diagnostic ZIP contains:

- a JSON manifest with application, environment, file hash, and failure metadata;
- the extracted PDF text, when extraction was possible;
- the processing traceback;
- sharing and privacy instructions.

The original PDF is **not included by default**. Review `extracted_text.txt` before sharing because ledger text can contain confidential customer and financial information.

To report an error:

1. Open GitHub Issue #1 or create a separate parser defect issue.
2. State the Tally Prime version and ledger report/export options used.
3. Describe what was expected and what the application produced.
4. Attach the diagnostic ZIP after reviewing it for confidential information.
5. Attach a sanitized PDF only when necessary and legally permitted.

## 5. Minimum beta validation checklist

For every PDF layout tested, confirm:

- customer/ledger name is correct;
- opening and closing balances match Tally;
- transaction dates and voucher numbers match;
- invoice, receipt, debit note, and credit note classification is correct;
- debit/credit direction is correct;
- multi-page rows are not lost or duplicated;
- FIFO allocations match the agreed accounting method;
- credit-period due dates are correct;
- interest days, rate, rounding, and totals are correct;
- the Excel workbook opens without repair warnings;
- print layout and number formatting are accountant-readable;
- a malformed or unsupported PDF fails safely and produces diagnostics.

## 6. What to record during testing

Record the PDF layout, number of pages, number of transactions, expected closing balance, expected interest total, generated interest total, validation warnings, and diagnostic ZIP name. Do not place unredacted customer data in a public issue.
