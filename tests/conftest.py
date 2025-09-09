"""
Pytest configuration and fixtures for Explicto-Nummus tests.
"""
import pytest
import tempfile
import os
from database import BankDatabase


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    db = BankDatabase(db_path)
    yield db
    db.close()
    os.unlink(db_path)


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return """Description,,Summary Amt.
Beginning balance as of 04/01/2024,,"10,541.95"
Total credits,,"28,789.38"
Total debits,,"-31,711.25"
Ending balance as of 09/01/2025,,"7,620.08"

Date,Description,Amount,Running Bal.
04/01/2024,Beginning balance as of 04/01/2024,,"10,541.95"
05/10/2024,"Test Credit Card Payment","-25.49","10,516.46"
05/24/2024,"Test Deposit","100.00","10,616.46"
06/01/2024,"Test Transfer","-50.00","10,566.46"
"""


@pytest.fixture
def sample_csv_file(sample_csv_data, tmp_path):
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test_statement.csv"
    csv_file.write_text(sample_csv_data)
    return str(csv_file)
