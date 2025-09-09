"""
Unit tests for CSV parsing functionality.
"""
import pytest
import pandas as pd
from database import BankDatabase


class TestCSVParsing:
    """Test cases for CSV parsing functionality."""
    
    def test_parse_bank_of_america_format(self, temp_db):
        """Test parsing Bank of America CSV format."""
        csv_data = """Description,,Summary Amt.
Beginning balance as of 04/01/2024,,"10,541.95"
Total credits,,"28,789.38"
Total debits,,"-31,711.25"
Ending balance as of 09/01/2025,,"7,620.08"

Date,Description,Amount,Running Bal.
04/01/2024,Beginning balance as of 04/01/2024,,"10,541.95"
05/10/2024,"BANK OF AMERICA CREDIT CARD Bill Payment","-25.49","10,516.46"
05/24/2024,"Bank of America Credit Card Bill Payment","-59.09","10,457.37"
06/21/2024,"Cash App DES:* Cash App ID:T32TNF2D14NX7X4","35.00","10,374.19"
"""
        
        # Create temporary CSV file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            csv_path = f.name
        
        try:
            result = temp_db.import_csv_data(
                csv_path, "Bank of America", "1234567890", "Test Account"
            )
            
            assert result['success'] is True
            assert result['transactions_imported'] == 3  # Skip beginning balance row
            
            # Verify transactions
            transactions = temp_db.get_all_transactions()
            assert len(transactions) == 3
            
            # Check first transaction (most recent)
            assert transactions[0]['description'] == "Cash App DES:* Cash App ID:T32TNF2D14NX7X4"
            assert transactions[0]['amount'] == 35.0
            assert transactions[0]['transaction_type'] == 'credit'
            assert transactions[0]['balance_after'] == 10374.19
            
        finally:
            import os
            os.unlink(csv_path)
    
    def test_parse_amount_variations(self, temp_db):
        """Test parsing various amount formats."""
        test_cases = [
            ("100.00", 100.0),
            ("1,234.56", 1234.56),
            ("-100.00", -100.0),
            ("-1,234.56", -1234.56),
            ('"1,234.56"', 1234.56),
            ("(1,234.56)", -1234.56),
            ("", 0.0),
            ("nan", 0.0),
            (None, 0.0),
        ]
        
        for input_amount, expected in test_cases:
            result = temp_db.parse_amount(input_amount)
            assert float(result) == expected, f"Failed for input: {input_amount}"
    
    def test_parse_date_variations(self, temp_db):
        """Test parsing various date formats."""
        test_cases = [
            ("04/01/2024", "2024-04-01"),
            ("12/31/2023", "2023-12-31"),
            ("01/01/2025", "2025-01-01"),
            ("2024-04-01", "2024-04-01"),
        ]
        
        for input_date, expected in test_cases:
            result = temp_db.parse_date(input_date)
            assert result == expected, f"Failed for input: {input_date}"
    
    def test_skip_summary_rows(self, temp_db):
        """Test that summary rows are properly skipped."""
        csv_data = """Description,,Summary Amt.
Beginning balance as of 04/01/2024,,"10,541.95"
Total credits,,"28,789.38"
Total debits,,"-31,711.25"
Ending balance as of 09/01/2025,,"7,620.08"

Date,Description,Amount,Running Bal.
04/01/2024,Beginning balance as of 04/01/2024,,"10,541.95"
05/10/2024,"Valid Transaction","-25.49","10,516.46"
Total credits,,"28,789.38"
05/24/2024,"Another Valid Transaction","100.00","10,616.46"
Ending balance as of 09/01/2025,,"7,620.08"
"""
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            csv_path = f.name
        
        try:
            result = temp_db.import_csv_data(
                csv_path, "Test Bank", "1234567890", "Test Account"
            )
            
            assert result['success'] is True
            assert result['transactions_imported'] == 2  # Two valid transactions
            
            transactions = temp_db.get_all_transactions()
            assert len(transactions) == 2
            
            # Verify no summary rows were imported
            descriptions = [t['description'] for t in transactions]
            assert "Beginning balance as of 04/01/2024" not in descriptions
            assert "Total credits" not in descriptions
            assert "Ending balance as of 09/01/2025" not in descriptions
            
        finally:
            import os
            os.unlink(csv_path)
    
    def test_handle_empty_rows(self, temp_db):
        """Test handling of empty rows in CSV."""
        csv_data = """Description,,Summary Amt.
Beginning balance as of 04/01/2024,,"10,541.95"

Date,Description,Amount,Running Bal.
04/01/2024,Beginning balance as of 04/01/2024,,"10,541.95"

05/10/2024,"Valid Transaction","-25.49","10,516.46"

05/24/2024,"Another Valid Transaction","100.00","10,616.46"

"""
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            csv_path = f.name
        
        try:
            result = temp_db.import_csv_data(
                csv_path, "Test Bank", "1234567890", "Test Account"
            )
            
            assert result['success'] is True
            assert result['transactions_imported'] == 1  # Only valid transactions (empty rows are skipped)
            
        finally:
            import os
            os.unlink(csv_path)
    
    def test_handle_malformed_data(self, temp_db):
        """Test handling of malformed data in CSV."""
        csv_data = """Description,,Summary Amt.
Beginning balance as of 04/01/2024,,"10,541.95"

Date,Description,Amount,Running Bal.
04/01/2024,Beginning balance as of 04/01/2024,,"10,541.95"
05/10/2024,"Valid Transaction","-25.49","10,516.46"
invalid-date,"Invalid Date Transaction","100.00","10,616.46"
05/24/2024,"Valid Transaction","invalid-amount","10,716.46"
05/25/2024,"Valid Transaction","50.00","10,766.46"
"""
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            csv_path = f.name
        
        try:
            result = temp_db.import_csv_data(
                csv_path, "Test Bank", "1234567890", "Test Account"
            )
            
            # Should succeed but with some errors
            assert result['success'] is True
            assert result['transactions_imported'] == 1  # Only valid transactions (empty rows are skipped)
            assert len(result['errors']) == 1  # One malformed row (invalid amount is handled gracefully)
            
            # Verify only valid transactions were imported
            transactions = temp_db.get_all_transactions()
            assert len(transactions) == 1
            
        finally:
            import os
            os.unlink(csv_path)
