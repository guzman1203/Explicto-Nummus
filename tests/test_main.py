"""
Unit tests for main.py CLI functionality.
"""
import pytest
import subprocess
import sys
import os
from unittest.mock import patch, MagicMock


class TestMainCLI:
    """Test cases for main.py CLI functionality."""
    
    def test_help_command(self):
        """Test that help command works."""
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert "Bank Statement CSV to Database" in result.stdout
    
    def test_test_command(self):
        """Test the test command."""
        result = subprocess.run([sys.executable, "main.py", "test"], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert "Testing with sample CSV file" in result.stdout
        assert "Import successful" in result.stdout
    
    def test_list_command(self):
        """Test the list command."""
        result = subprocess.run([sys.executable, "main.py", "list", "--limit", "5"], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert "All Transactions" in result.stdout
    
    def test_summary_command(self):
        """Test the summary command."""
        result = subprocess.run([sys.executable, "main.py", "summary"], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert "Monthly Summary" in result.stdout
    
    def test_balance_command(self):
        """Test the balance command."""
        result = subprocess.run([sys.executable, "main.py", "balance"], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert "Balance History" in result.stdout
    
    def test_import_command_invalid_file(self):
        """Test import command with invalid file."""
        result = subprocess.run([sys.executable, "main.py", "import", 
                               "nonexistent.csv", "Test Bank", "1234567890"], 
                              capture_output=True, text=True)
        assert result.returncode == 1
        assert "not found" in result.stderr or "not found" in result.stdout
    
    def test_import_command_valid_file(self, sample_csv_file):
        """Test import command with valid file."""
        result = subprocess.run([sys.executable, "main.py", "import", 
                               sample_csv_file, "Test Bank", "1234567890", 
                               "--account-name", "Test Account"], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert "Import successful" in result.stdout
    
    def test_invalid_command(self):
        """Test invalid command."""
        result = subprocess.run([sys.executable, "main.py", "invalid"], 
                              capture_output=True, text=True)
        assert result.returncode == 2  # argparse returns 2 for invalid commands
        assert "invalid choice" in result.stderr
