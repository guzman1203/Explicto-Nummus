"""
Unit tests for database operations.
"""
import pytest
from decimal import Decimal
from database import BankDatabase


class TestBankDatabase:
    """Test cases for BankDatabase class."""
    
    def test_database_initialization(self, temp_db):
        """Test database initialization and table creation."""
        assert temp_db.db_path is not None
        assert temp_db.conn is not None
        
        # Check if tables exist
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'banks' in tables
        assert 'accounts' in tables
        assert 'transactions' in tables
    
    def test_get_or_create_bank(self, temp_db):
        """Test bank creation and retrieval."""
        # Create new bank
        bank_id = temp_db.get_or_create_bank("Test Bank")
        assert bank_id == 1
        
        # Get existing bank
        bank_id_2 = temp_db.get_or_create_bank("Test Bank")
        assert bank_id_2 == bank_id
        
        # Create another bank
        bank_id_3 = temp_db.get_or_create_bank("Another Bank")
        assert bank_id_3 == 2
    
    def test_get_or_create_account(self, temp_db):
        """Test account creation and retrieval."""
        # Create bank first
        bank_id = temp_db.get_or_create_bank("Test Bank")
        
        # Create new account
        account_id = temp_db.get_or_create_account(
            bank_id, "1234567890", "Test Account", "checking"
        )
        assert account_id == 1
        
        # Get existing account
        account_id_2 = temp_db.get_or_create_account(
            bank_id, "1234567890", "Test Account", "checking"
        )
        assert account_id_2 == account_id
    
    def test_parse_amount(self, temp_db):
        """Test amount parsing functionality."""
        # Test positive amounts
        assert temp_db.parse_amount("100.00") == Decimal('100.00')
        assert temp_db.parse_amount("1,234.56") == Decimal('1234.56')
        assert temp_db.parse_amount('"1,234.56"') == Decimal('1234.56')
        
        # Test negative amounts
        assert temp_db.parse_amount("-100.00") == Decimal('-100.00')
        assert temp_db.parse_amount("-1,234.56") == Decimal('-1234.56')
        assert temp_db.parse_amount("(1,234.56)") == Decimal('-1234.56')
        
        # Test edge cases
        assert temp_db.parse_amount("") == Decimal('0.00')
        assert temp_db.parse_amount(None) == Decimal('0.00')
        assert temp_db.parse_amount("nan") == Decimal('0.00')
    
    def test_parse_date(self, temp_db):
        """Test date parsing functionality."""
        # Test MM/DD/YYYY format
        assert temp_db.parse_date("04/01/2024") == "2024-04-01"
        assert temp_db.parse_date("12/31/2023") == "2023-12-31"
        
        # Test YYYY-MM-DD format
        assert temp_db.parse_date("2024-04-01") == "2024-04-01"
        
        # Test invalid date
        with pytest.raises(ValueError):
            temp_db.parse_date("invalid-date")
    
    def test_get_all_transactions_empty(self, temp_db):
        """Test getting transactions from empty database."""
        transactions = temp_db.get_all_transactions()
        assert transactions == []
    
    def test_get_monthly_summary_empty(self, temp_db):
        """Test getting monthly summary from empty database."""
        summary = temp_db.get_monthly_summary()
        assert summary == []
    
    def test_get_account_balance_history_empty(self, temp_db):
        """Test getting balance history from empty database."""
        history = temp_db.get_account_balance_history()
        assert history == []
    
    def test_import_csv_data_success(self, temp_db, sample_csv_file):
        """Test successful CSV import."""
        result = temp_db.import_csv_data(
            sample_csv_file, "Test Bank", "1234567890", "Test Account"
        )
        
        assert result['success'] is True
        assert result['transactions_imported'] == 3  # 3 valid transactions
        assert 'bank_id' in result
        assert 'account_id' in result
        
        # Verify data was inserted
        transactions = temp_db.get_all_transactions()
        assert len(transactions) == 3
        
        # Check transaction details
        assert transactions[0]['bank_name'] == "Test Bank"
        assert transactions[0]['account_name'] == "Test Account"
        assert transactions[0]['transaction_type'] == 'debit'
        assert transactions[0]['amount'] == -50.0
    
    def test_import_csv_data_invalid_file(self, temp_db):
        """Test CSV import with invalid file."""
        result = temp_db.import_csv_data(
            "nonexistent.csv", "Test Bank", "1234567890", "Test Account"
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_monthly_summary_after_import(self, temp_db, sample_csv_file):
        """Test monthly summary after importing data."""
        temp_db.import_csv_data(
            sample_csv_file, "Test Bank", "1234567890", "Test Account"
        )
        
        summary = temp_db.get_monthly_summary()
        assert len(summary) == 2  # April and May 2024
        
        # Check May 2024 summary
        may_summary = next(s for s in summary if s['month'] == '2024-05')
        assert may_summary['total_income'] == 100.0
        assert may_summary['total_expenses'] == 25.49  # One debit of 25.49 (June is separate month)
        assert may_summary['net_amount'] == 74.51  # 100.00 - 25.49
    
    def test_account_balance_history_after_import(self, temp_db, sample_csv_file):
        """Test balance history after importing data."""
        temp_db.import_csv_data(
            sample_csv_file, "Test Bank", "1234567890", "Test Account"
        )
        
        history = temp_db.get_account_balance_history()
        assert len(history) == 3
        
        # Check that balances are in descending order by date
        assert history[0]['transaction_date'] == '2024-06-01'
        assert history[0]['balance_after'] == 10566.46
