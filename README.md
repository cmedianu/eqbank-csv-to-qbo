# QuickBooks Helper - EQ Bank CSV to QBO Converter

Convert EQ Bank CSV transaction downloads to QBO format for importing into QuickBooks.

## The Problem

EQ Bank only provides transaction downloads in CSV format, but QuickBooks expects QBO files for easy import. Additionally, when setting up online banking in QuickBooks 2010 (and possibly other older versions), EQ Bank doesn't appear in the bank list since it's a newer institution.

## The Solution

This tool converts EQ Bank's CSV export files into QBO format that QuickBooks can import via double-click.

### Workaround for Online Banking Setup

When setting up online banking in QuickBooks 2010:
1. EQ Bank won't be in the institution list (it didn't exist when QB 2010 was released)
2. You can still set up online banking, but it's finicky
3. QuickBooks will think the account is from TD Bank (because we use TD Bank's institution ID `300000100` in the QBO files)
4. **This is fine** - the account number is correct, and transactions will import properly

The bank name mismatch is purely cosmetic and doesn't affect functionality.

## Usage

### Step 1: Download Your Transactions from EQ Bank

Download your transaction history as CSV. EQ Bank names the downloaded file in the format `{account_number} Details.csv` (e.g., `123456789 Details.csv`). The converter will automatically parse the account number from this filename.

### Step 2: Convert to QBO

**On Windows:**
```cmd
eqbankcsv2qbo.bat "123456789 Details.csv"
```

**On Linux/Mac/WSL:**
```bash
./eqbankcsv2qbo.sh "123456789 Details.csv"
```

**Or using uv directly:**
```bash
uv run eqbankcsv2qbo.py "123456789 Details.csv"
```

### Step 3: Import into QuickBooks

Double-click the generated `.qbo` file (e.g., `123456789 Details.qbo`) and QuickBooks will open and prompt you to import the transactions.

## Requirements

- Python 3 (for running the converter)
- [uv](https://github.com/astral-sh/uv) (Python package runner - automatically handles dependencies)
- QuickBooks 2010 or later

## CSV Format

The script expects EQ Bank CSV files with these columns:
- **Transfer date** - Transaction date (YYYY-MM-DD format)
- **Description** - Transaction description
- **Amount** - Transaction amount (e.g., `$7326.38` or `-$486.07`)
- **Balance** - Account balance after transaction

The account number is extracted from the filename.

## Notes

- The converter uses TD Bank's institution ID (`BANKID: 300000100`) for compatibility
- Currency is set to CAD (Canadian dollars)
- All transactions are marked as CHECKING account type
- Timezone is set to Eastern Time (EST)
- The generated QBO files are compatible with QuickBooks 2010 and likely newer versions

## Tested With

- QuickBooks 2010
- EQ Bank CSV exports (2025-2026)

## Troubleshooting

**Problem:** QuickBooks doesn't recognize the account

**Solution:** Make sure the account number in your CSV filename matches your QuickBooks account number exactly.

---

**Problem:** Import crashes or fails

**Solution:** Check that your CSV has all required columns: `Transfer date`, `Description`, `Amount`, `Balance`

---

**Problem:** QuickBooks says it's a TD Bank account

**Solution:** This is expected and harmless. The institution ID is borrowed from TD Bank for compatibility, but your transactions will import correctly.
