import sqlite3
import pandas as pd
from datetime import datetime
from decimal import Decimal
import re
from typing import List, Dict, Any, Optional

class BankDatabase:
    def __init__(self, db_path: str = "bank_data.db"):
        """Initialize the database connection and create tables."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_tables()
    
    def create_tables(self):
        """Create the database tables according to the schema."""
        cursor = self.conn.cursor()
        
        # Create Banks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS banks (
                bank_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create Accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank_id INTEGER NOT NULL,
                account_number VARCHAR(255) NOT NULL,
                account_name VARCHAR(255),
                account_type VARCHAR(50) DEFAULT 'checking',
                opening_balance DECIMAL(15,2) DEFAULT 0.00,
                current_balance DECIMAL(15,2),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bank_id) REFERENCES banks(bank_id)
            )
        """)
        
        # Create Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                transaction_date DATE NOT NULL,
                description TEXT,
                amount DECIMAL(15,2) NOT NULL,
                transaction_type VARCHAR(10) NOT NULL,
                reference_number VARCHAR(255),
                balance_after DECIMAL(15,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(account_id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_date ON transactions(transaction_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_account_id ON transactions(account_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_account_date ON transactions(account_id, transaction_date)")
        
        self.conn.commit()
    
    def get_or_create_bank(self, bank_name: str) -> int:
        """Get existing bank ID or create new bank record."""
        cursor = self.conn.cursor()
        
        # Check if bank exists
        cursor.execute("SELECT bank_id FROM banks WHERE bank_name = ?", (bank_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            # Create new bank
            cursor.execute(
                "INSERT INTO banks (bank_name) VALUES (?)",
                (bank_name,)
            )
            self.conn.commit()
            return cursor.lastrowid
    
    def get_or_create_account(self, bank_id: int, account_number: str, 
                            account_name: str = None, account_type: str = 'checking') -> int:
        """Get existing account ID or create new account record."""
        cursor = self.conn.cursor()
        
        # Check if account exists
        cursor.execute(
            "SELECT account_id FROM accounts WHERE bank_id = ? AND account_number = ?",
            (bank_id, account_number)
        )
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            # Create new account
            cursor.execute("""
                INSERT INTO accounts (bank_id, account_number, account_name, account_type)
                VALUES (?, ?, ?, ?)
            """, (bank_id, account_number, account_name, account_type))
            self.conn.commit()
            return cursor.lastrowid
    
    def parse_amount(self, amount_str: str) -> Decimal:
        """Parse amount string and return as Decimal."""
        if not amount_str or amount_str.strip() == '' or str(amount_str).strip() == 'nan':
            return Decimal('0.00')
        
        # Convert to string and remove commas and quotes
        cleaned = str(amount_str).replace(',', '').replace('"', '').strip()
        
        # Handle negative amounts
        if cleaned.startswith('-'):
            return Decimal(cleaned)
        elif cleaned.startswith('(') and cleaned.endswith(')'):
            # Handle (amount) format for negative
            return -Decimal(cleaned[1:-1])
        else:
            return Decimal(cleaned)
    
    def parse_date(self, date_str: str) -> str:
        """Parse date string and return in YYYY-MM-DD format."""
        try:
            # Handle MM/DD/YYYY format
            if '/' in date_str:
                date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                return date_obj.strftime('%Y-%m-%d')
            else:
                # Try other common formats
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
        except ValueError:
            raise ValueError(f"Unable to parse date: {date_str}")
    
    def import_csv_data(self, csv_file_path: str, bank_name: str, 
                       account_number: str, account_name: str = None) -> Dict[str, Any]:
        """Import bank statement data from CSV file."""
        try:
            # Read CSV file with proper handling of the stmt.csv format
            # Skip the first 6 rows (summary data) and use row 7 as header
            df = pd.read_csv(csv_file_path, skiprows=6)
            
            # Get or create bank and account
            bank_id = self.get_or_create_bank(bank_name)
            account_id = self.get_or_create_account(bank_id, account_number, account_name)
            
            # Process transactions
            transactions_imported = 0
            errors = []
            
            # Process each transaction
            for i, row in df.iterrows():
                try:
                    # Skip empty rows
                    if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                        continue
                    
                    # Extract transaction data
                    date_str = str(row.iloc[0]).strip()
                    description = str(row.iloc[1]).strip() if not pd.isna(row.iloc[1]) else ''
                    amount_str = str(row.iloc[2]).strip() if not pd.isna(row.iloc[2]) else '0'
                    balance_str = str(row.iloc[3]).strip() if len(row) > 3 and not pd.isna(row.iloc[3]) else None
                    
                    # Skip summary rows that might still be present
                    if ('Total' in description or 'Beginning' in description or 
                        'Ending' in description or 'Summary' in description):
                        continue
                    
                    # Skip header row if it appears in data
                    if date_str == 'Date' or description == 'Description':
                        continue
                    
                    # Skip rows with NaN amounts (like the beginning balance row)
                    if pd.isna(row.iloc[2]) or str(row.iloc[2]).strip() == 'nan':
                        continue
                    
                    # Parse and validate data
                    transaction_date = self.parse_date(date_str)
                    amount = self.parse_amount(amount_str)
                    balance_after = self.parse_amount(balance_str) if balance_str else None
                    
                    # Determine transaction type
                    transaction_type = 'credit' if amount >= 0 else 'debit'
                    
                    # Insert transaction
                    cursor = self.conn.cursor()
                    cursor.execute("""
                        INSERT INTO transactions 
                        (account_id, transaction_date, description, amount, transaction_type, balance_after)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (account_id, transaction_date, description, float(amount), transaction_type, float(balance_after) if balance_after else None))
                    
                    transactions_imported += 1
                    
                except Exception as e:
                    errors.append(f"Row {i+7}: {str(e)}")  # +7 because we skipped 6 rows
                    continue
            
            # Update account current balance
            if transactions_imported > 0:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT balance_after FROM transactions 
                    WHERE account_id = ? 
                    ORDER BY transaction_date DESC, transaction_id DESC 
                    LIMIT 1
                """, (account_id,))
                result = cursor.fetchone()
                if result and result[0]:
                    cursor.execute("""
                        UPDATE accounts SET current_balance = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE account_id = ?
                    """, (float(result[0]), account_id))
            
            self.conn.commit()
            
            return {
                'success': True,
                'transactions_imported': transactions_imported,
                'errors': errors,
                'bank_id': bank_id,
                'account_id': account_id
            }
            
        except Exception as e:
            self.conn.rollback()
            return {
                'success': False,
                'error': str(e),
                'transactions_imported': 0,
                'errors': []
            }
    
    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Get all transactions with bank and account information."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                b.bank_name,
                a.account_name,
                t.transaction_date,
                t.description,
                t.amount,
                t.transaction_type,
                t.balance_after
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            JOIN banks b ON a.bank_id = b.bank_id
            ORDER BY t.transaction_date DESC
        """)
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_monthly_summary(self) -> List[Dict[str, Any]]:
        """Get monthly summary of income and expenses."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', transaction_date) as month,
                SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN transaction_type = 'debit' THEN ABS(amount) ELSE 0 END) as total_expenses,
                SUM(amount) as net_amount
            FROM transactions
            GROUP BY strftime('%Y-%m', transaction_date)
            ORDER BY month DESC
        """)
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_account_balance_history(self, account_id: int = None) -> List[Dict[str, Any]]:
        """Get account balance history."""
        cursor = self.conn.cursor()
        
        if account_id:
            cursor.execute("""
                SELECT 
                    a.account_name,
                    t.transaction_date,
                    t.balance_after,
                    t.description
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.account_id = ?
                ORDER BY t.transaction_date DESC
            """, (account_id,))
        else:
            cursor.execute("""
                SELECT 
                    a.account_name,
                    t.transaction_date,
                    t.balance_after,
                    t.description
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                ORDER BY t.transaction_date DESC
            """)
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
