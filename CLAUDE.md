# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QuickBooks Helper tool for converting EQ Bank CSV transaction exports to QBO (QuickBooks) format. The bank switched from providing QBO files (which can be double-clicked to import) to CSV files. This tool bridges that gap.

## Running the Converter

**Primary script:** `eqbankcsv2qbo.py`

```bash
# Using uv (recommended)
uv run eqbankcsv2qbo.py "123456789 Details.csv"

# Or use wrapper scripts
./eqbankcsv2qbo.sh "123456789 Details.csv"    # Linux/Mac
eqbankcsv2qbo.bat "123456789 Details.csv"     # Windows
```

The script generates a `.qbo` file that can be double-clicked to import into QuickBooks.

## Input/Output Format

**Input CSV format** (from EQ Bank):
- Filename contains account number: `{account_number} Details.csv`
- Columns: `Transfer date`, `Description`, `Amount`, `Balance`
- Dates in `YYYY-MM-DD` format
- Amounts like `$7326.38` or `-$486.07`
- Newest transactions first (reversed during processing)

**Output QBO format** (OFX/SGML):
- Account number extracted from input filename → `<ACCTID>` tag
- Transaction description → `<NAME>` tag (Payee field in QuickBooks)
- Each transaction gets unique FITID: `{YY}{DayOfYear}{10-digit-index}`
- Dates formatted as `YYYYMMDD020000[-5:EST]`

## Key Architecture

**Main conversion flow:**
1. Extract account number from filename using regex `(\d+)`
2. Parse CSV with standard DictReader
3. Reverse transaction order (CSV is newest-first, QBO expects chronological)
4. Generate OFX header and wrapper structure
5. Convert each transaction to OFX `<STMTTRN>` block
6. Add final balance and close OFX structure

**Hardcoded values in QBO output:**
- `<BANKID>300000100` - Bank routing/institution ID (inherited from TD Bank format)
- `<CURDEF>CAD` - Currency (Canadian dollars)
- `<ACCTTYPE>CHECKING` - Account type
- `<INTU.BID>00002` - Intuit Bank ID
- Timezone: `[-5:EST]` - Eastern Time

These can be modified if needed for different banks or account types.

## Known Limitations

**MEMO field experimentation:**
The OFX spec supports a `<MEMO>` tag that should map to comment/memo fields, but QuickBooks behavior varies:
- Empty `<NAME>` + `<MEMO>` → QuickBooks crashes on import
- Both `<NAME>` and `<MEMO>` → QuickBooks ignores the MEMO field
- Current solution: Description goes only in `<NAME>` (Payee field)

If experimenting with MEMO field variations, create separate script versions (e.g., `eqbankcsv2qbo-memo-*.py`) rather than modifying the working version.
