# Testing Guide for Explicto-Nummus

This document provides comprehensive information about the testing strategy and implementation for the Explicto-Nummus bank statement CSV to database system.

## Test Suite Overview

The test suite consists of **34 tests** with **97% code coverage**, organized into three main categories:

- **Unit Tests** (18 tests): Test individual components in isolation
- **Integration Tests** (8 tests): Test end-to-end workflows
- **CLI Tests** (8 tests): Test command-line interface functionality

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest fixtures and configuration
├── test_database.py            # Database operation unit tests
├── test_csv_parsing.py         # CSV parsing unit tests
├── test_integration.py         # Integration tests
└── test_main.py               # CLI functionality tests
```

## Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Categories
```bash
# Unit tests only
python run_tests.py unit

# Integration tests only
python run_tests.py integration
```

### Run Individual Test Files
```bash
# Database tests
pytest tests/test_database.py -v

# CSV parsing tests
pytest tests/test_csv_parsing.py -v

# Integration tests
pytest tests/test_integration.py -v

# CLI tests
pytest tests/test_main.py -v
```

### Run with Coverage
```bash
pytest --cov=database --cov-report=html
```

## Test Categories

### 1. Unit Tests (`test_database.py`)

Tests individual database operations and utility functions:

- **Database Initialization**: Table creation and schema validation
- **Bank Management**: Creating and retrieving bank records
- **Account Management**: Creating and retrieving account records
- **Data Parsing**: Amount and date parsing functions
- **Query Functions**: Empty database query behavior
- **CSV Import**: Successful and failed import scenarios
- **Monthly Summaries**: Financial calculation accuracy
- **Balance History**: Transaction ordering and balance tracking

### 2. CSV Parsing Tests (`test_csv_parsing.py`)

Tests CSV file parsing and data extraction:

- **Bank of America Format**: Real-world CSV format compatibility
- **Amount Variations**: Different number formats and edge cases
- **Date Variations**: Multiple date format support
- **Summary Row Skipping**: Proper filtering of non-transaction data
- **Empty Row Handling**: Graceful handling of empty CSV rows
- **Malformed Data**: Error handling for invalid data

### 3. Integration Tests (`test_integration.py`)

Tests complete workflows and system interactions:

- **Full Import and Query Workflow**: End-to-end data processing
- **Multiple Accounts**: Same bank, different accounts
- **Multiple Banks**: Different bank support
- **Balance Calculations**: Accurate account balance updates
- **Monthly Summary Calculations**: Financial reporting accuracy
- **Transaction Ordering**: Proper chronological sorting
- **Error Handling and Rollback**: Database consistency on failures

### 4. CLI Tests (`test_main.py`)

Tests command-line interface functionality:

- **Help Command**: Proper help text display
- **Test Command**: Sample data processing
- **List Command**: Transaction listing functionality
- **Summary Command**: Monthly summary display
- **Balance Command**: Balance history display
- **Import Command**: CSV file import functionality
- **Invalid Commands**: Error handling for invalid inputs

## Test Fixtures

### Database Fixtures
- `temp_db`: Creates a temporary SQLite database for each test
- `sample_csv_data`: Provides test CSV data
- `sample_csv_file`: Creates temporary CSV file for testing

### Test Data
The test suite uses realistic bank statement data that mimics the actual `stmt.csv` format:

```csv
Description,,Summary Amt.
Beginning balance as of 04/01/2024,,"10,541.95"
Total credits,,"28,789.38"
Total debits,,"-31,711.25"
Ending balance as of 09/01/2025,,"7,620.08"

Date,Description,Amount,Running Bal.
04/01/2024,Beginning balance as of 04/01/2024,,"10,541.95"
05/10/2024,"Test Credit Card Payment","-25.49","10,516.46"
05/24/2024,"Test Deposit","100.00","10,616.46"
06/01/2024,"Test Transfer","-50.00","10,566.46"
```

## Coverage Report

The test suite achieves **97% code coverage** with only 4 lines uncovered:

- Line 164: Error handling in CSV parsing
- Line 179: Error handling in CSV parsing  
- Line 183: Error handling in CSV parsing
- Line 285: Error handling in balance history query

## Test Configuration

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=database
    --cov-report=term-missing
    --cov-report=html:htmlcov
```

### Test Runner (`run_tests.py`)
Custom test runner with:
- Categorized test execution
- Coverage reporting
- HTML coverage reports
- Clear success/failure messaging

## Best Practices Implemented

### 1. Test Isolation
- Each test uses a fresh temporary database
- No shared state between tests
- Proper cleanup after each test

### 2. Comprehensive Coverage
- Tests cover happy path and error scenarios
- Edge cases and boundary conditions tested
- Real-world data formats validated

### 3. Clear Test Names
- Descriptive test method names
- Clear test documentation
- Logical test organization

### 4. Fixture Usage
- Reusable test data
- Consistent test setup
- Proper resource management

### 5. Assertion Quality
- Specific assertions with clear error messages
- Multiple assertions per test where appropriate
- Validation of both success and failure cases

## Continuous Integration Considerations

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: python run_tests.py
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

### Pre-commit Hooks
```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: python run_tests.py
        language: system
        pass_filenames: false
        always_run: true
```

## Debugging Tests

### Running Individual Tests
```bash
# Run specific test
pytest tests/test_database.py::TestBankDatabase::test_parse_amount -v

# Run with print statements
pytest tests/test_database.py::TestBankDatabase::test_parse_amount -v -s

# Run with debugging
pytest tests/test_database.py::TestBankDatabase::test_parse_amount -v --pdb
```

### Test Output Analysis
- Use `-v` flag for verbose output
- Use `--tb=short` for concise error traces
- Check HTML coverage report for uncovered lines
- Use `--pdb` for interactive debugging

## Future Test Enhancements

### Planned Additions
1. **Performance Tests**: Large dataset processing
2. **Concurrency Tests**: Multi-threaded database access
3. **Memory Tests**: Resource usage validation
4. **API Tests**: Future REST API endpoints
5. **UI Tests**: Future web interface testing

### Test Data Expansion
1. **Multiple Bank Formats**: Chase, Wells Fargo, etc.
2. **Edge Case Data**: Very large amounts, special characters
3. **International Formats**: Different date/number formats
4. **Corrupted Data**: Malformed CSV files

## Conclusion

The Explicto-Nummus test suite provides comprehensive coverage of all system functionality with a focus on reliability, maintainability, and real-world compatibility. The 97% code coverage and 34 passing tests ensure the system is robust and ready for production use.
