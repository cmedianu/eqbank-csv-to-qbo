#!/usr/bin/env python3
"""
Convert EQ Bank CSV files to QBO format for QuickBooks import.
Usage: uv run eqbankcsv2qbo.py <csv_file>
"""

import csv
import sys
import re
from datetime import datetime
from pathlib import Path


def extract_account_number(filename):
    """Extract account number from filename like '400000395 Details.csv'"""
    match = re.match(r'(\d+)', Path(filename).stem)
    if match:
        return match.group(1)
    return "000000000"  # Default if no account number found


def parse_amount(amount_str):
    """Parse amount string like '$7326.38' or '-$486.07' to float"""
    # Remove $ and commas, keep negative sign
    cleaned = amount_str.replace('$', '').replace(',', '')
    return float(cleaned)


def format_date_ofx(date_str):
    """Convert date like '2026-01-06' to OFX format '20260106020000[-5:EST]'"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%Y%m%d020000[-5:EST]')


def generate_fitid(date_str, index):
    """Generate a unique transaction ID"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    # Format: YYDDDHHHHHHSSSS where DDD is day of year
    day_of_year = date_obj.timetuple().tm_yday
    return f"{date_obj.strftime('%y')}{day_of_year:03d}{index:010d}"


def csv_to_qbo(csv_file):
    """Convert CSV file to QBO format"""
    account_number = extract_account_number(csv_file)

    # Read CSV file
    transactions = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Transfer date']:  # Skip empty rows
                transactions.append(row)

    if not transactions:
        print("No transactions found in CSV file")
        return None

    # Reverse to get chronological order (CSV is newest first)
    transactions.reverse()

    # Get date range
    start_date = transactions[0]['Transfer date']
    end_date = transactions[-1]['Transfer date']
    final_balance = parse_amount(transactions[-1]['Balance'])

    # Generate current timestamp for DTSERVER
    now = datetime.now()
    dtserver = now.strftime('%Y%m%d%H%M%S[-5:EST]')
    trnuid = f"QWEB - {now.strftime('%Y%m%d%H%M%S%f')[:17]}"

    # Start building QBO content
    qbo_lines = [
        "OFXHEADER:100",
        "DATA:OFXSGML",
        "VERSION:102",
        "SECURITY:TYPE1",
        "ENCODING:USASCII",
        "CHARSET:1252",
        "COMPRESSION:NONE",
        "OLDFILEUID:NONE",
        "NEWFILEUID:NONE",
        "",
        "<OFX>",
        "<SIGNONMSGSRSV1>",
        "<SONRS>",
        "<STATUS>",
        "<CODE>0",
        "<SEVERITY>INFO",
        "<MESSAGE>OK",
        "</STATUS>",
        f"<DTSERVER>{dtserver}",
        "<USERKEY>--NoUserKey--",
        "<LANGUAGE>ENG",
        "<INTU.BID>00002",
        "</SONRS>",
        "</SIGNONMSGSRSV1>",
        "<BANKMSGSRSV1>",
        "<STMTTRNRS>",
        f"<TRNUID>{trnuid}",
        "<STATUS>",
        "<CODE>0",
        "<SEVERITY>INFO",
        "<MESSAGE>OK",
        "</STATUS>",
        "<STMTRS>",
        "<CURDEF>CAD",
        "<BANKACCTFROM>",
        "<BANKID>300000100",
        f"<ACCTID>{account_number}",
        "<ACCTTYPE>CHECKING",
        "</BANKACCTFROM>",
        "<BANKTRANLIST>",
        f"<DTSTART>{datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')}",
        f"<DTEND>{format_date_ofx(end_date)}",
    ]

    # Add transactions
    for idx, txn in enumerate(transactions, 1):
        amount = parse_amount(txn['Amount'])
        trntype = "CREDIT" if amount > 0 else "DEBIT"

        qbo_lines.extend([
            "<STMTTRN>",
            f"<TRNTYPE>{trntype}",
            f"<DTPOSTED>{format_date_ofx(txn['Transfer date'])}",
            f"<TRNAMT>{amount:.2f}",
            f"<FITID>{generate_fitid(txn['Transfer date'], idx)}",
            f"<NAME>{txn['Description'][:32]}",  # Truncate to 32 chars
            "</STMTTRN>",
        ])

    # Close out the QBO file
    qbo_lines.extend([
        "</BANKTRANLIST>",
        "<LEDGERBAL>",
        f"<BALAMT>{final_balance:.2f}",
        f"<DTASOF>{format_date_ofx(end_date)}",
        "</LEDGERBAL>",
        "<AVAILBAL>",
        f"<BALAMT>{final_balance:.2f}",
        f"<DTASOF>{format_date_ofx(end_date)}",
        "</AVAILBAL>",
        "</STMTRS>",
        "</STMTTRNRS>",
        "</BANKMSGSRSV1>",
        "</OFX>",
    ])

    return '\n'.join(qbo_lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run eqbankcsv2qbo.py <csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]

    if not Path(csv_file).exists():
        print(f"Error: File '{csv_file}' not found")
        sys.exit(1)

    # Generate QBO content
    qbo_content = csv_to_qbo(csv_file)

    if qbo_content:
        # Create output filename
        output_file = Path(csv_file).with_suffix('.qbo')

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(qbo_content)

        print(f"Successfully converted {csv_file} to {output_file}")
        print(f"You can now double-click {output_file} to import into QuickBooks")
    else:
        print("Conversion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
