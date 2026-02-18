"""
Unit Tests untuk Quality Checker Module
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.quality_checker import DataQualityChecker, QualityReport, QualityIssue, QualityLevel


class TestDataQualityChecker(unittest.TestCase):
    """Test DataQualityChecker class"""
    
    def setUp(self):
        """Set up test data"""
        self.clean_data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['x', 'y', 'z', 'w', 'v'],
            'C': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        
        self.dirty_data = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5, np.nan],
            'B': ['x', 'y', 'z', 'x', 'y', 'z'],  # Duplicates
            'C': [1, 2, 3, 1000, 5, 6],  # Outlier
            'Contact Number': ['08123456789', 'invalid', '', '08123456789', '123', '08198765432'],
            'Date Created': ['2024-01-15', 'invalid', '2024-02-20', '2024-03-10', '', '2024-04-25']
        })
    
    def test_initialization(self):
        """Test initialization"""
        checker = DataQualityChecker(self.clean_data)
        self.assertIsNotNone(checker.df)
        self.assertEqual(len(checker.issues), 0)
    
    def test_check_completeness_clean(self):
        """Test completeness check on clean data"""
        checker = DataQualityChecker(self.clean_data)
        checker.check_completeness()
        
        # Should have no completeness issues
        completeness_issues = [i for i in checker.issues if i.issue_type == 'completeness']
        self.assertEqual(len(completeness_issues), 0)
        
        # Score should be 100
        self.assertEqual(checker.scores.get('completeness'), 100)
    
    def test_check_completeness_dirty(self):
        """Test completeness check on dirty data"""
        checker = DataQualityChecker(self.dirty_data)
        checker.check_completeness()
        
        # Should have completeness issues
        completeness_issues = [i for i in checker.issues if i.issue_type == 'completeness']
        self.assertGreater(len(completeness_issues), 0)
        
        # Score should be less than 100
        self.assertLess(checker.scores.get('completeness', 100), 100)
    
    def test_check_uniqueness_clean(self):
        """Test uniqueness check on clean data"""
        checker = DataQualityChecker(self.clean_data)
        checker.check_uniqueness()
        
        # Should have no duplicates
        uniqueness_issues = [i for i in checker.issues if i.issue_type == 'uniqueness']
        self.assertEqual(len(uniqueness_issues), 0)
    
    def test_check_uniqueness_dirty(self):
        """Test uniqueness check on dirty data"""
        checker = DataQualityChecker(self.dirty_data)
        checker.check_uniqueness()
        
        # Should have duplicate issues
        uniqueness_issues = [i for i in checker.issues if i.issue_type == 'uniqueness']
        self.assertGreater(len(uniqueness_issues), 0)
    
    def test_check_validity_phone(self):
        """Test phone validation"""
        checker = DataQualityChecker(self.dirty_data)
        checker.check_validity()
        
        # Should have phone validity issues
        validity_issues = [i for i in checker.issues if i.issue_type == 'validity' and i.column == 'Contact Number']
        self.assertGreater(len(validity_issues), 0)
    
    def test_check_validity_date(self):
        """Test date validation"""
        checker = DataQualityChecker(self.dirty_data)
        checker.check_validity()
        
        # Should have date validity issues
        validity_issues = [i for i in checker.issues if i.issue_type == 'validity' and i.column == 'Date Created']
        self.assertGreater(len(validity_issues), 0)
    
    def test_run_all_checks(self):
        """Test running all checks"""
        checker = DataQualityChecker(self.dirty_data)
        result = checker.run_all_checks()
        
        self.assertIn('overall_score', result)
        self.assertIn('quality_level', result)
        self.assertIn('total_issues', result)
        self.assertIn('scores', result)
        self.assertIn('issues', result)
        self.assertIn('recommendations', result)
    
    def test_overall_score_calculation(self):
        """Test overall score calculation"""
        checker = DataQualityChecker(self.clean_data)
        result = checker.run_all_checks()
        
        # Clean data should have high score
        self.assertGreaterEqual(result['overall_score'], 90)
    
    def test_quality_level_excellent(self):
        """Test quality level for excellent data"""
        checker = DataQualityChecker(self.clean_data)
        result = checker.run_all_checks()
        
        self.assertEqual(result['quality_level'], 'excellent')
    
    def test_quality_level_poor(self):
        """Test quality level for poor data"""
        # Create very poor quality data
        poor_data = pd.DataFrame({
            'A': [np.nan] * 10,
            'B': ['x'] * 10  # All duplicates
        })
        
        checker = DataQualityChecker(poor_data)
        result = checker.run_all_checks()
        
        self.assertIn(result['quality_level'], ['poor', 'critical'])
    
    def test_get_issues_by_severity(self):
        """Test getting issues by severity"""
        checker = DataQualityChecker(self.dirty_data)
        checker.run_all_checks()
        
        critical_issues = checker.get_issues_by_severity('critical')
        warning_issues = checker.get_issues_by_severity('warning')
        info_issues = checker.get_issues_by_severity('info')
        
        self.assertIsInstance(critical_issues, list)
        self.assertIsInstance(warning_issues, list)
        self.assertIsInstance(info_issues, list)
    
    def test_get_issues_by_column(self):
        """Test getting issues by column"""
        checker = DataQualityChecker(self.dirty_data)
        checker.run_all_checks()
        
        contact_issues = checker.get_issues_by_column('Contact Number')
        self.assertIsInstance(contact_issues, list)
    
    def test_fix_common_issues(self):
        """Test fixing common issues"""
        # Create data with whitespace issues
        whitespace_data = pd.DataFrame({
            'A': ['  test  ', 'hello', '  world  '],
            'B': [1, 2, 3]
        })
        
        checker = DataQualityChecker(whitespace_data)
        fixed_df = checker.fix_common_issues()
        
        # Check whitespace is trimmed
        self.assertEqual(fixed_df['A'].iloc[0], 'test')
        self.assertEqual(fixed_df['A'].iloc[2], 'world')


class TestQualityReport(unittest.TestCase):
    """Test QualityReport class"""
    
    def setUp(self):
        """Set up test data"""
        self.data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['x', 'y', 'z', 'w', 'v']
        })
        
        self.checker = DataQualityChecker(self.data)
        self.report = QualityReport(self.checker)
    
    def test_generate_summary_card(self):
        """Test generating summary card"""
        card = self.report.generate_summary_card()
        
        self.assertIn('score', card)
        self.assertIn('status', card)
        self.assertIn('color', card)
        self.assertIn('total_issues', card)
    
    def test_generate_detailed_report(self):
        """Test generating detailed report"""
        report_text = self.report.generate_detailed_report()
        
        self.assertIsInstance(report_text, str)
        self.assertIn('DATA QUALITY REPORT', report_text)
        self.assertIn('Overall Score', report_text)


class TestQualityLevel(unittest.TestCase):
    """Test QualityLevel enum"""
    
    def test_quality_levels(self):
        """Test quality level values"""
        self.assertEqual(QualityLevel.EXCELLENT.value, 'excellent')
        self.assertEqual(QualityLevel.GOOD.value, 'good')
        self.assertEqual(QualityLevel.FAIR.value, 'fair')
        self.assertEqual(QualityLevel.POOR.value, 'poor')
        self.assertEqual(QualityLevel.CRITICAL.value, 'critical')


if __name__ == '__main__':
    unittest.main()
