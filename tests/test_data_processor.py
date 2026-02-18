"""
Unit Tests untuk Data Processor Module
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processor import DataProcessor, BatchProcessor


class TestDataProcessor(unittest.TestCase):
    """Test DataProcessor class"""
    
    def setUp(self):
        """Set up test data"""
        self.sample_data = pd.DataFrame({
            'SC Order No/Track ID/CSRM No': ['AO123', 'PDA456', 'WSA789', 'OTHER'],
            'Workorder': ['WO001.0', 'WO002.0', 'WO003.0', 'WO004.0'],
            'Date Created': ['2024-01-15 10:00:00', '2024-02-20 11:00:00', 
                            '2024-01-25 12:00:00', '2024-03-10 13:00:00'],
            'CRM Order Type': ['CREATE', 'MIGRATE', 'CREATE', 'UPDATE'],
            'Status': ['WAPPR', 'COMP', 'WAPPR', 'PEND'],
            'Customer Name': ['Customer A', 'Customer B', 'Customer C', 'Customer D'],
            'Contact Number': ['08123456789', '', '08198765432', ''],
            'Workzone': ['Zone 1', 'Zone 2', 'Zone 1', 'Zone 3']
        })
    
    def test_initialization(self):
        """Test DataProcessor initialization"""
        processor = DataProcessor(mode='WSA')
        self.assertEqual(processor.mode, 'WSA')
        self.assertIsNone(processor.df_raw)
    
    def test_load_data(self):
        """Test loading data"""
        processor = DataProcessor(mode='WSA')
        result = processor.load_data(self.sample_data)
        
        self.assertIsInstance(result, DataProcessor)
        self.assertIsNotNone(processor.df_raw)
        self.assertEqual(len(processor.df_raw), 4)
    
    def test_clean_common(self):
        """Test common cleaning"""
        processor = DataProcessor(mode='WSA')
        processor.load_data(self.sample_data).clean_common()
        
        # Check Workorder cleaned
        self.assertNotIn('.0', str(processor.df_processed['Workorder'].iloc[0]))
        
        # Check Date Created parsed
        self.assertIn('Date Created DT', processor.df_processed.columns)
    
    def test_filter_wsa(self):
        """Test WSA filtering"""
        processor = DataProcessor(mode='WSA')
        df_result = (processor
            .load_data(self.sample_data)
            .clean_common()
            .filter_by_mode()
            .df_processed)
        
        # Should filter out 'OTHER' row
        self.assertEqual(len(df_result), 3)
        
        # Should only have CREATE/MIGRATE
        self.assertTrue(all(df_result['CRM Order Type'].isin(['CREATE', 'MIGRATE'])))
    
    def test_filter_modoroso(self):
        """Test MODOROSO filtering"""
        modoroso_data = pd.DataFrame({
            'SC Order No/Track ID/CSRM No': ['ORDER-MO-001', 'ORDER-DO-002', 'ORDER-REG'],
            'Workorder': ['WO001', 'WO002', 'WO003'],
            'Date Created': ['2024-01-15', '2024-02-20', '2024-03-10'],
            'CRM Order Type': ['CREATE', 'CREATE', 'CREATE'],
            'Status': ['WAPPR', 'WAPPR', 'WAPPR'],
            'Customer Name': ['A', 'B', 'C'],
            'Contact Number': ['08123456789', '08123456790', '08123456791'],
            'Workzone': ['Zone 1', 'Zone 2', 'Zone 3']
        })
        
        processor = DataProcessor(mode='MODOROSO')
        df_result = (processor
            .load_data(modoroso_data)
            .clean_common()
            .filter_by_mode()
            .df_processed)
        
        # Should filter to only MO/DO
        self.assertEqual(len(df_result), 2)
        
        # Check Mitra column added
        self.assertIn('Mitra', df_result.columns)
        self.assertEqual(df_result['Mitra'].iloc[0], 'TSEL')
    
    def test_filter_wappr(self):
        """Test WAPPR filtering"""
        processor = DataProcessor(mode='WAPPR')
        df_result = (processor
            .load_data(self.sample_data)
            .clean_common()
            .filter_by_mode()
            .df_processed)
        
        # Should only have WAPPR status
        self.assertTrue(all(df_result['Status'] == 'WAPPR'))
    
    def test_filter_by_month(self):
        """Test month filtering"""
        processor = DataProcessor(mode='WSA')
        df_result = (processor
            .load_data(self.sample_data)
            .clean_common()
            .filter_by_mode()
            .filter_by_month([1])  # January only
            .df_processed)
        
        # Should have only January data
        self.assertEqual(len(df_result), 2)
    
    def test_remove_duplicates(self):
        """Test duplicate removal"""
        processor = DataProcessor(mode='WSA')
        df_result = (processor
            .load_data(self.sample_data)
            .clean_common()
            .filter_by_mode()
            .remove_duplicates(['AO123'])  # AO123 already exists
            .df_final)
        
        # Should remove AO123
        self.assertEqual(len(df_result), 2)
        self.assertNotIn('AO123', df_result['SC Order No/Track ID/CSRM No'].values)
    
    def test_finalize(self):
        """Test finalization"""
        processor = DataProcessor(mode='WSA')
        df_result = (processor
            .load_data(self.sample_data)
            .clean_common()
            .filter_by_mode()
            .finalize())
        
        # Check temporary columns removed
        self.assertNotIn('Date Created DT', df_result.columns)
        self.assertNotIn('Date Created Display', df_result.columns)
    
    def test_get_stats(self):
        """Test getting stats"""
        processor = DataProcessor(mode='WSA')
        processor.load_data(self.sample_data)
        
        stats = processor.get_stats()
        self.assertIn('raw_rows', stats)
        self.assertEqual(stats['raw_rows'], 4)
    
    def test_process_all(self):
        """Test complete processing pipeline"""
        processor = DataProcessor(mode='WSA')
        df_result = processor.process_all(
            self.sample_data,
            months=[1, 2],
            existing_ids=[]
        )
        
        self.assertIsInstance(df_result, pd.DataFrame)
        self.assertGreater(len(df_result), 0)


class TestBatchProcessor(unittest.TestCase):
    """Test BatchProcessor class"""
    
    def setUp(self):
        """Set up test data"""
        self.large_data = pd.DataFrame({
            'SC Order No/Track ID/CSRM No': [f'AO{i:04d}' for i in range(100)],
            'Workorder': [f'WO{i:04d}.0' for i in range(100)],
            'Date Created': ['2024-01-15'] * 100,
            'CRM Order Type': ['CREATE'] * 100,
            'Status': ['WAPPR'] * 100,
            'Customer Name': [f'Customer {i}' for i in range(100)],
            'Contact Number': ['08123456789'] * 100,
            'Workzone': ['Zone 1'] * 100
        })
    
    def test_batch_processing(self):
        """Test batch processing"""
        processor = DataProcessor(mode='WSA')
        batch_processor = BatchProcessor(processor, batch_size=25)
        
        result = batch_processor.process_chunks(self.large_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
    
    def test_get_errors(self):
        """Test getting errors"""
        processor = DataProcessor(mode='WSA')
        batch_processor = BatchProcessor(processor)
        
        errors = batch_processor.get_errors()
        self.assertIsInstance(errors, list)


if __name__ == '__main__':
    unittest.main()
