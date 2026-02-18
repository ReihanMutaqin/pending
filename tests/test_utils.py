"""
Unit Tests untuk Utils Module
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    parse_date, format_date, get_bulan_indonesia, get_current_period,
    clean_string, normalize_phone, validate_phone, extract_order_id,
    clean_dataframe, reorder_columns, get_column_stats,
    validate_file_extension, validate_required_columns,
    memory_usage, chunk_list
)


class TestDateUtils(unittest.TestCase):
    """Test date utility functions"""
    
    def test_parse_date_valid(self):
        """Test parsing valid dates"""
        result = parse_date('2024-01-15 10:30:00')
        self.assertIsNotNone(result)
        self.assertEqual(result.day, 15)
        self.assertEqual(result.month, 1)
    
    def test_parse_date_invalid(self):
        """Test parsing invalid dates"""
        result = parse_date('invalid_date')
        self.assertIsNone(result)
    
    def test_parse_date_with_suffix(self):
        """Test parsing date with .0 suffix"""
        result = parse_date('2024-01-15.0')
        self.assertIsNotNone(result)
    
    def test_format_date(self):
        """Test formatting dates"""
        date_obj = datetime(2024, 1, 15, 10, 30, 0)
        result = format_date(date_obj, '%d/%m/%Y')
        self.assertEqual(result, '15/01/2024')
    
    def test_format_date_none(self):
        """Test formatting None date"""
        result = format_date(None)
        self.assertEqual(result, '')
    
    def test_get_bulan_indonesia(self):
        """Test getting Indonesian month names"""
        self.assertEqual(get_bulan_indonesia(1), 'Januari')
        self.assertEqual(get_bulan_indonesia(12), 'Desember')
        self.assertEqual(get_bulan_indonesia(1, singkat=True), 'Jan')
    
    def test_get_current_period(self):
        """Test getting current period"""
        curr, prev = get_current_period()
        self.assertIsInstance(curr, int)
        self.assertIsInstance(prev, int)
        self.assertTrue(1 <= curr <= 12)
        self.assertTrue(1 <= prev <= 12)


class TestStringUtils(unittest.TestCase):
    """Test string utility functions"""
    
    def test_clean_string_basic(self):
        """Test basic string cleaning"""
        self.assertEqual(clean_string('  test  '), 'test')
        self.assertEqual(clean_string('TEST', uppercase=True), 'TEST')
    
    def test_clean_string_nan(self):
        """Test cleaning NaN values"""
        self.assertEqual(clean_string(np.nan), '')
        self.assertEqual(clean_string(None), '')
    
    def test_clean_string_suffix(self):
        """Test removing .0 suffix"""
        self.assertEqual(clean_string('123.0'), '123')
    
    def test_normalize_phone(self):
        """Test phone normalization"""
        self.assertEqual(normalize_phone('08123456789'), '628123456789')
        self.assertEqual(normalize_phone('8123456789'), '628123456789')
        self.assertEqual(normalize_phone('+62 812-3456-789'), '628123456789')
    
    def test_validate_phone_valid(self):
        """Test validating valid phones"""
        self.assertTrue(validate_phone('628123456789'))
        self.assertTrue(validate_phone('08123456789'))
    
    def test_validate_phone_invalid(self):
        """Test validating invalid phones"""
        self.assertFalse(validate_phone('123'))
        self.assertFalse(validate_phone(''))
    
    def test_extract_order_id(self):
        """Test extracting order ID"""
        self.assertEqual(extract_order_id('ORDER_123_456'), 'ORDER')
        self.assertEqual(extract_order_id('ORDER123'), 'ORDER123')


class TestDataFrameUtils(unittest.TestCase):
    """Test DataFrame utility functions"""
    
    def setUp(self):
        """Set up test DataFrame"""
        self.df = pd.DataFrame({
            'A': [1, 2, np.nan, 4],
            'B': ['x', 'y', 'z', ''],
            'C': [1.0, 2.0, 3.0, 4.0]
        })
    
    def test_clean_dataframe(self):
        """Test cleaning DataFrame"""
        result = clean_dataframe(self.df)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 4)
    
    def test_reorder_columns(self):
        """Test reordering columns"""
        result = reorder_columns(self.df, ['C', 'A', 'B'])
        self.assertEqual(list(result.columns), ['C', 'A', 'B'])
    
    def test_reorder_columns_partial(self):
        """Test reordering with partial list"""
        result = reorder_columns(self.df, ['C', 'A'])
        self.assertEqual(list(result.columns)[0], 'C')
        self.assertEqual(list(result.columns)[1], 'A')
    
    def test_get_column_stats(self):
        """Test getting column stats"""
        stats = get_column_stats(self.df)
        self.assertEqual(stats['total_rows'], 4)
        self.assertEqual(stats['total_columns'], 3)
        self.assertIn('A', stats['columns'])


class TestValidationUtils(unittest.TestCase):
    """Test validation utility functions"""
    
    def test_validate_file_extension_valid(self):
        """Test validating valid file extensions"""
        self.assertTrue(validate_file_extension('test.xlsx'))
        self.assertTrue(validate_file_extension('test.csv'))
        self.assertTrue(validate_file_extension('test.xls'))
    
    def test_validate_file_extension_invalid(self):
        """Test validating invalid file extensions"""
        self.assertFalse(validate_file_extension('test.txt'))
        self.assertFalse(validate_file_extension('test.pdf'))
    
    def test_validate_required_columns_all_present(self):
        """Test validating when all columns present"""
        df = pd.DataFrame({'A': [1], 'B': [2], 'C': [3]})
        is_valid, missing = validate_required_columns(df, ['A', 'B'])
        self.assertTrue(is_valid)
        self.assertEqual(missing, [])
    
    def test_validate_required_columns_missing(self):
        """Test validating when columns missing"""
        df = pd.DataFrame({'A': [1], 'B': [2]})
        is_valid, missing = validate_required_columns(df, ['A', 'C'])
        self.assertFalse(is_valid)
        self.assertEqual(missing, ['C'])


class TestPerformanceUtils(unittest.TestCase):
    """Test performance utility functions"""
    
    def test_chunk_list(self):
        """Test chunking list"""
        lst = list(range(10))
        result = chunk_list(lst, 3)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], [0, 1, 2])
        self.assertEqual(result[-1], [9])
    
    def test_memory_usage(self):
        """Test memory usage calculation"""
        df = pd.DataFrame({'A': range(1000)})
        result = memory_usage(df)
        self.assertIn('B', result)  # Should contain unit


if __name__ == '__main__':
    unittest.main()
