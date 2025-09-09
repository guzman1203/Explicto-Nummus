# Explicto-Nummus - Bank Statement CSV to Database

A Python application that imports bank statement CSV files into a SQLite database for analysis and querying.

## Features

- **CSV Import**: Import bank statement CSV files from various banks
- **Database Storage**: Store data in SQLite with proper schema design
- **Transaction Queries**: View all transactions with filtering options
- **Monthly Summaries**: Get income/expense summaries by month
- **Balance History**: Track account balance changes over time
- **Data Validation**: Robust error handling and data validation

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install pandas
   ```

## Usage

### Basic Commands

**Test with sample data:**
```bash
python main.py test
```

**Import a CSV file:**
```bash
python main.py import "path/to/your/statement.csv" "Bank Name" "Account Number" --account-name "Account Name"
```

**List all transactions:**
```bash
python main.py list
python main.py list --limit 10  # Show only first 10 transactions
```

**Show monthly summary:**
```bash
python main.py summary
```

**Show balance history:**
```bash
python main.py balance
python main.py balance --account-id 1  # Specific account
```

### Supported CSV Format

The system currently supports CSV files with the following structure:
- Summary rows at the top (automatically skipped)
- Header row: "Date,Description,Amount,Running Bal."
- Transaction data with MM/DD/YYYY date format
- Comma-separated amounts (e.g., "1,234.56")

## Database Schema

The system creates three main tables:

- **banks**: Bank information
- **accounts**: Account details linked to banks
- **transactions**: Individual transaction records

## Example Output

```
📊 All Transactions (5 total)
Date         Bank                 Account              Type     Amount       Balance      Description
----------------------------------------------------------------------------------------------------
2025-08-26   Bank of America      William Gonzalez Checking debit    $-9.99       $7,620.08    Online Banking payment to CRD
2025-08-26   Bank of America      William Gonzalez Checking debit    $-667.45     $7,630.07    Online Banking payment to CRD
2025-08-22   Bank of America      William Gonzalez Checking credit   $1,778.11    $8,297.52    ALPHASTAFF SHR DES:PAYROLL ID:

📈 Monthly Summary
Month      Income          Expenses        Net
------------------------------------------------------------
2025-08    $4,109.27       $-2,125.10      $6,234.37
2025-07    $3,556.22       $-1,514.29      $5,070.51
```

## Version 1 Features

- ✅ SQLite database with core tables
- ✅ CSV import functionality
- ✅ Basic querying capabilities
- ✅ Data validation and error handling
- ✅ Monthly summaries
- ✅ Balance history tracking

## Future Versions

- Categorization system
- Budget tracking
- Advanced analytics
- Web dashboard
- Data visualization
