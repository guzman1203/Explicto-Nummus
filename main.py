#!/usr/bin/env python3
"""
Bank Statement CSV to Database - Main Application
Version 1 Prototype

This script provides a command-line interface for importing bank statement CSV files
into a SQLite database and running basic queries.
"""

import argparse
import sys
import os
from database import BankDatabase
import json

def print_transactions(transactions):
    """Print transactions in a formatted table."""
    if not transactions:
        print("No transactions found.")
        return
    
    print(f"\n{'Date':<12} {'Bank':<20} {'Account':<20} {'Type':<8} {'Amount':<12} {'Balance':<12} {'Description'}")
    print("-" * 100)
    
    for txn in transactions:
        amount_str = f"${txn['amount']:,.2f}"
        balance_str = f"${txn['balance_after']:,.2f}" if txn['balance_after'] else "N/A"
        print(f"{txn['transaction_date']:<12} {txn['bank_name']:<20} {txn['account_name']:<20} "
              f"{txn['transaction_type']:<8} {amount_str:<12} {balance_str:<12} {txn['description'][:30]}")

def print_monthly_summary(summary):
    """Print monthly summary in a formatted table."""
    if not summary:
        print("No monthly data found.")
        return
    
    print(f"\n{'Month':<10} {'Income':<15} {'Expenses':<15} {'Net':<15}")
    print("-" * 60)
    
    for month in summary:
        income_str = f"${month['total_income']:,.2f}"
        expenses_str = f"${month['total_expenses']:,.2f}"
        net_str = f"${month['net_amount']:,.2f}"
        print(f"{month['month']:<10} {income_str:<15} {expenses_str:<15} {net_str:<15}")

def import_csv_file(csv_path, bank_name, account_number, account_name=None):
    """Import a CSV file into the database."""
    if not os.path.exists(csv_path):
        print(f"Error: CSV file '{csv_path}' not found.")
        return False
    
    print(f"Importing CSV file: {csv_path}")
    print(f"Bank: {bank_name}")
    print(f"Account: {account_number}")
    if account_name:
        print(f"Account Name: {account_name}")
    
    db = BankDatabase()
    result = db.import_csv_data(csv_path, bank_name, account_number, account_name)
    
    if result['success']:
        print(f"\n[SUCCESS] Import successful!")
        print(f"   Transactions imported: {result['transactions_imported']}")
        if result['errors']:
            print(f"   Errors encountered: {len(result['errors'])}")
            for error in result['errors'][:5]:  # Show first 5 errors
                print(f"     - {error}")
            if len(result['errors']) > 5:
                print(f"     ... and {len(result['errors']) - 5} more errors")
    else:
        print(f"\n[ERROR] Import failed: {result['error']}")
    
    db.close()
    return result['success']

def list_transactions(limit=None):
    """List all transactions."""
    db = BankDatabase()
    transactions = db.get_all_transactions()
    
    if limit:
        transactions = transactions[:limit]
    
    print(f"\n[DATA] All Transactions ({len(transactions)} total)")
    print_transactions(transactions)
    db.close()

def show_monthly_summary():
    """Show monthly summary."""
    db = BankDatabase()
    summary = db.get_monthly_summary()
    
    print(f"\n[SUMMARY] Monthly Summary")
    print_monthly_summary(summary)
    db.close()

def show_balance_history(account_id=None):
    """Show account balance history."""
    db = BankDatabase()
    history = db.get_account_balance_history(account_id)
    
    print(f"\n[BALANCE] Balance History")
    if not history:
        print("No balance history found.")
    else:
        print(f"{'Date':<12} {'Account':<20} {'Balance':<15} {'Description'}")
        print("-" * 70)
        for entry in history:
            balance_str = f"${entry['balance_after']:,.2f}" if entry['balance_after'] else "N/A"
            print(f"{entry['transaction_date']:<12} {entry['account_name']:<20} "
                  f"{balance_str:<15} {entry['description'][:30]}")
    
    db.close()

def main():
    parser = argparse.ArgumentParser(description='Bank Statement CSV to Database - Version 1')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import CSV file')
    import_parser.add_argument('csv_file', help='Path to CSV file')
    import_parser.add_argument('bank_name', help='Name of the bank')
    import_parser.add_argument('account_number', help='Account number')
    import_parser.add_argument('--account-name', help='Account name (optional)')
    
    # List transactions command
    list_parser = subparsers.add_parser('list', help='List all transactions')
    list_parser.add_argument('--limit', type=int, help='Limit number of transactions to show')
    
    # Monthly summary command
    summary_parser = subparsers.add_parser('summary', help='Show monthly summary')
    
    # Balance history command
    balance_parser = subparsers.add_parser('balance', help='Show balance history')
    balance_parser.add_argument('--account-id', type=int, help='Specific account ID (optional)')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test with sample CSV file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'import':
        success = import_csv_file(args.csv_file, args.bank_name, args.account_number, args.account_name)
        sys.exit(0 if success else 1)
    
    elif args.command == 'list':
        list_transactions(args.limit)
    
    elif args.command == 'summary':
        show_monthly_summary()
    
    elif args.command == 'balance':
        show_balance_history(args.account_id)
    
    elif args.command == 'test':
        print("[TEST] Testing with sample CSV file...")
        csv_path = "bank-statements/stmt.csv"
        success = import_csv_file(csv_path, "Bank of America", "1234567890", "William Gonzalez Checking")
        if success:
            print("\n[DATA] Sample transactions:")
            list_transactions(10)
            print("\n[SUMMARY] Sample monthly summary:")
            show_monthly_summary()

if __name__ == "__main__":
    main()
