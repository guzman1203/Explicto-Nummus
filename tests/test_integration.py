"""
Integration tests for end-to-end workflows.
"""
import pytest
from database import BankDatabase


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_import_and_query_workflow(self, temp_db, sample_csv_file):
        """Test complete workflow from CSV import to querying."""
        # Import CSV data
        result = temp_db.import_csv_data(
            sample_csv_file, "Test Bank", "1234567890", "Test Account"
        )
        
        assert result['success'] is True
        assert result['transactions_imported'] == 3
        
        # Test all query functions
        transactions = temp_db.get_all_transactions()
        assert len(transactions) == 3
        
        monthly_summary = temp_db.get_monthly_summary()
        assert len(monthly_summary) == 2  # April and May 2024
        
        balance_history = temp_db.get_account_balance_history()
        assert len(balance_history) == 3
        
        # Verify data consistency
        assert all(t['bank_name'] == "Test Bank" for t in transactions)
        assert all(t['account_name'] == "Test Account" for t in transactions)
    
    def test_multiple_accounts_same_bank(self, temp_db, sample_csv_file):
        """Test importing data for multiple accounts from the same bank."""
        # Import first account
        result1 = temp_db.import_csv_data(
            sample_csv_file, "Test Bank", "1111111111", "Account 1"
        )
        assert result1['success'] is True
        
        # Import second account
        result2 = temp_db.import_csv_data(
            sample_csv_file, "Test Bank", "2222222222", "Account 2"
        )
        assert result2['success'] is True
        
        # Verify both accounts exist
        transactions = temp_db.get_all_transactions()
        assert len(transactions) == 6  # 3 transactions per account
        
        # Verify bank is shared
        bank_names = set(t['bank_name'] for t in transactions)
        assert bank_names == {"Test Bank"}
        
        # Verify accounts are different
        account_names = set(t['account_name'] for t in transactions)
        assert account_names == {"Account 1", "Account 2"}
    
    def test_multiple_banks(self, temp_db, sample_csv_file):
        """Test importing data for multiple banks."""
        # Import first bank
        result1 = temp_db.import_csv_data(
            sample_csv_file, "Bank A", "1111111111", "Account 1"
        )
        assert result1['success'] is True
        
        # Import second bank
        result2 = temp_db.import_csv_data(
            sample_csv_file, "Bank B", "2222222222", "Account 2"
        )
        assert result2['success'] is True
        
        # Verify both banks exist
        transactions = temp_db.get_all_transactions()
        assert len(transactions) == 6  # 3 transactions per bank
        
        bank_names = set(t['bank_name'] for t in transactions)
        assert bank_names == {"Bank A", "Bank B"}
    
    def test_account_balance_calculation(self, temp_db, sample_csv_file):
        """Test that account balance is calculated correctly."""
        result = temp_db.import_csv_data(
            sample_csv_file, "Test Bank", "1234567890", "Test Account"
        )
        
        assert result['success'] is True
        
        # Check account balance
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT current_balance FROM accounts WHERE account_id = ?", (result['account_id'],))
        current_balance = cursor.fetchone()[0]
        
        # Should be the balance from the last transaction
        assert current_balance == 10566.46
    
    def test_monthly_summary_calculations(self, temp_db, sample_csv_file):
        """Test that monthly summary calculations are correct."""
        result = temp_db.import_csv_data(
            sample_csv_file, "Test Bank", "1234567890", "Test Account"
        )
        
        assert result['success'] is True
        
        monthly_summary = temp_db.get_monthly_summary()
        
        # Check May 2024 summary
        may_summary = next(s for s in monthly_summary if s['month'] == '2024-05')
        assert may_summary['total_income'] == 100.0  # One credit of 100.00
        assert may_summary['total_expenses'] == 25.49  # One debit of 25.49 (June is separate month)
        assert may_summary['net_amount'] == 74.51  # 100.00 - 25.49
    
    def test_transaction_ordering(self, temp_db, sample_csv_file):
        """Test that transactions are ordered correctly."""
        result = temp_db.import_csv_data(
            sample_csv_file, "Test Bank", "1234567890", "Test Account"
        )
        
        assert result['success'] is True
        
        transactions = temp_db.get_all_transactions()
        
        # Should be ordered by date descending (most recent first)
        dates = [t['transaction_date'] for t in transactions]
        assert dates == ['2024-06-01', '2024-05-24', '2024-05-10']
    
    def test_balance_history_ordering(self, temp_db, sample_csv_file):
        """Test that balance history is ordered correctly."""
        result = temp_db.import_csv_data(
            sample_csv_file, "Test Bank", "1234567890", "Test Account"
        )
        
        assert result['success'] is True
        
        balance_history = temp_db.get_account_balance_history()
        
        # Should be ordered by date descending
        dates = [h['transaction_date'] for h in balance_history]
        assert dates == ['2024-06-01', '2024-05-24', '2024-05-10']
        
        # Balances should be in descending order
        balances = [h['balance_after'] for h in balance_history]
        assert balances == [10566.46, 10616.46, 10516.46]
    
    def test_error_handling_and_rollback(self, temp_db):
        """Test error handling and database rollback."""
        # Try to import non-existent file
        result = temp_db.import_csv_data(
            "nonexistent.csv", "Test Bank", "1234567890", "Test Account"
        )
        
        assert result['success'] is False
        assert 'error' in result
        
        # Verify no data was inserted
        transactions = temp_db.get_all_transactions()
        assert len(transactions) == 0
        
        # Verify no bank or account was created
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM banks")
        bank_count = cursor.fetchone()[0]
        assert bank_count == 0
        
        cursor.execute("SELECT COUNT(*) FROM accounts")
        account_count = cursor.fetchone()[0]
        assert account_count == 0
