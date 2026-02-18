"""
Data Quality Checker untuk WSA Fulfillment Pro
Berisi fungsi-fungsi untuk memeriksa dan memastikan kualitas data
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.utils import logger, validate_phone, parse_date, clean_string
from config.settings import QUALITY_CONFIG


class QualityLevel(Enum):
    """Level kualitas data"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class QualityIssue:
    """Struktur untuk menyimpan issue kualitas"""
    column: str
    issue_type: str
    severity: str
    message: str
    affected_rows: int
    affected_indices: List[int]
    suggestion: str


class DataQualityChecker:
    """
    Checker untuk kualitas data
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Inisialisasi DataQualityChecker
        
        Args:
            df: DataFrame yang akan dicek
        """
        self.df = df.copy()
        self.issues: List[QualityIssue] = []
        self.scores: Dict[str, float] = {}
        self.recommendations: List[str] = []
        
    def run_all_checks(self) -> Dict[str, Any]:
        """
        Jalankan semua pengecekan kualitas
        
        Returns:
            Dictionary hasil pengecekan
        """
        logger.info("Running all quality checks...")
        
        self.issues = []
        self.scores = {}
        self.recommendations = []
        
        # Run individual checks
        self.check_completeness()
        self.check_uniqueness()
        self.check_consistency()
        self.check_validity()
        self.check_accuracy()
        
        # Calculate overall score
        overall_score = self._calculate_overall_score()
        quality_level = self._determine_quality_level(overall_score)
        
        # Generate recommendations
        self._generate_recommendations()
        
        result = {
            'overall_score': round(overall_score, 2),
            'quality_level': quality_level.value,
            'total_issues': len(self.issues),
            'critical_issues': len([i for i in self.issues if i.severity == 'critical']),
            'warning_issues': len([i for i in self.issues if i.severity == 'warning']),
            'info_issues': len([i for i in self.issues if i.severity == 'info']),
            'scores': self.scores,
            'issues': self._issues_to_dict(),
            'recommendations': self.recommendations,
            'checked_at': pd.Timestamp.now().isoformat()
        }
        
        logger.info(f"Quality check completed. Score: {overall_score:.2f}, Issues: {len(self.issues)}")
        
        return result
    
    def check_completeness(self) -> None:
        """Cek kelengkapan data (null values)"""
        if not QUALITY_CONFIG['check_nulls']:
            return
        
        null_counts = self.df.isnull().sum()
        total_rows = len(self.df)
        
        completeness_scores = []
        
        for col in self.df.columns:
            null_count = null_counts[col]
            null_pct = null_count / total_rows if total_rows > 0 else 0
            
            completeness = (1 - null_pct) * 100
            completeness_scores.append(completeness)
            
            if null_pct > QUALITY_CONFIG['null_threshold']:
                severity = 'critical' if null_pct > 0.5 else 'warning'
                
                issue = QualityIssue(
                    column=col,
                    issue_type='completeness',
                    severity=severity,
                    message=f"{null_count} null values ({null_pct*100:.2f}%)",
                    affected_rows=null_count,
                    affected_indices=self.df[self.df[col].isnull()].index.tolist(),
                    suggestion=f"Consider filling null values in '{col}' or removing rows with missing data"
                )
                
                self.issues.append(issue)
        
        self.scores['completeness'] = np.mean(completeness_scores) if completeness_scores else 100
    
    def check_uniqueness(self) -> None:
        """Cek keunikan data (duplicates)"""
        if not QUALITY_CONFIG['check_duplicates']:
            return
        
        total_rows = len(self.df)
        
        # Check full row duplicates
        duplicate_mask = self.df.duplicated()
        duplicate_count = duplicate_mask.sum()
        duplicate_pct = duplicate_count / total_rows if total_rows > 0 else 0
        
        uniqueness = (1 - duplicate_pct) * 100
        
        if duplicate_pct > QUALITY_CONFIG['duplicate_threshold']:
            severity = 'critical' if duplicate_pct > 0.2 else 'warning'
            
            issue = QualityIssue(
                column='all',
                issue_type='uniqueness',
                severity=severity,
                message=f"{duplicate_count} duplicate rows ({duplicate_pct*100:.2f}%)",
                affected_rows=duplicate_count,
                affected_indices=self.df[duplicate_mask].index.tolist(),
                suggestion="Remove duplicate rows to improve data quality"
            )
            
            self.issues.append(issue)
        
        self.scores['uniqueness'] = uniqueness
    
    def check_consistency(self) -> None:
        """Cek konsistensi data"""
        # Check for inconsistent formatting in string columns
        for col in self.df.select_dtypes(include=['object']).columns:
            values = self.df[col].dropna().astype(str)
            
            if len(values) == 0:
                continue
            
            # Check for mixed case
            upper_count = values.str.isupper().sum()
            lower_count = values.str.islower().sum()
            mixed_count = len(values) - upper_count - lower_count
            
            if mixed_count > 0 and upper_count > 0 and lower_count > 0:
                issue = QualityIssue(
                    column=col,
                    issue_type='consistency',
                    severity='warning',
                    message=f"Mixed case formatting detected",
                    affected_rows=mixed_count,
                    affected_indices=[],
                    suggestion=f"Standardize case formatting in '{col}'"
                )
                
                self.issues.append(issue)
            
            # Check for leading/trailing whitespace
            whitespace_mask = values != values.str.strip()
            whitespace_count = whitespace_mask.sum()
            
            if whitespace_count > 0:
                issue = QualityIssue(
                    column=col,
                    issue_type='consistency',
                    severity='info',
                    message=f"{whitespace_count} values with leading/trailing whitespace",
                    affected_rows=whitespace_count,
                    affected_indices=self.df[col].astype(str).str.strip() != self.df[col].astype(str).fillna('').index[whitespace_mask].tolist(),
                    suggestion=f"Trim whitespace in '{col}'"
                )
                
                self.issues.append(issue)
        
        self.scores['consistency'] = 100 - len([i for i in self.issues if i.issue_type == 'consistency']) * 5
        self.scores['consistency'] = max(0, self.scores['consistency'])
    
    def check_validity(self) -> None:
        """Cek validitas data"""
        # Check phone numbers
        if QUALITY_CONFIG['validate_phone'] and 'Contact Number' in self.df.columns:
            invalid_phones = []
            
            for idx, phone in self.df['Contact Number'].items():
                if pd.notna(phone) and str(phone).strip() != '':
                    if not validate_phone(str(phone)):
                        invalid_phones.append(idx)
            
            if invalid_phones:
                issue = QualityIssue(
                    column='Contact Number',
                    issue_type='validity',
                    severity='warning',
                    message=f"{len(invalid_phones)} invalid phone numbers",
                    affected_rows=len(invalid_phones),
                    affected_indices=invalid_phones,
                    suggestion="Validate and correct phone number format"
                )
                
                self.issues.append(issue)
        
        # Check dates
        if QUALITY_CONFIG['validate_dates'] and 'Date Created' in self.df.columns:
            invalid_dates = []
            
            for idx, date in self.df['Date Created'].items():
                if pd.notna(date) and str(date).strip() != '':
                    parsed = parse_date(str(date))
                    if parsed is None:
                        invalid_dates.append(idx)
            
            if invalid_dates:
                issue = QualityIssue(
                    column='Date Created',
                    issue_type='validity',
                    severity='warning',
                    message=f"{len(invalid_dates)} invalid dates",
                    affected_rows=len(invalid_dates),
                    affected_indices=invalid_dates,
                    suggestion="Validate and correct date format"
                )
                
                self.issues.append(issue)
        
        # Check SC Order No format
        if 'SC Order No/Track ID/CSRM No' in self.df.columns:
            invalid_orders = []
            
            for idx, order in self.df['SC Order No/Track ID/CSRM No'].items():
                order_str = clean_string(order, uppercase=True)
                # Check if contains required patterns
                if not any(pattern in order_str for pattern in ['AO', 'PDA', 'WSA', '-MO', '-DO']):
                    invalid_orders.append(idx)
            
            if invalid_orders:
                issue = QualityIssue(
                    column='SC Order No/Track ID/CSRM No',
                    issue_type='validity',
                    severity='info',
                    message=f"{len(invalid_orders)} orders without standard pattern",
                    affected_rows=len(invalid_orders),
                    affected_indices=invalid_orders,
                    suggestion="Verify order number format"
                )
                
                self.issues.append(issue)
        
        self.scores['validity'] = 100 - len([i for i in self.issues if i.issue_type == 'validity']) * 5
        self.scores['validity'] = max(0, self.scores['validity'])
    
    def check_accuracy(self) -> None:
        """Cek akurasi data"""
        # Check for suspicious values (outliers, etc.)
        for col in self.df.select_dtypes(include=[np.number]).columns:
            values = self.df[col].dropna()
            
            if len(values) < 10:
                continue
            
            # Simple outlier detection using IQR
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = values[(values < lower_bound) | (values > upper_bound)]
            
            if len(outliers) > 0:
                outlier_pct = len(outliers) / len(values) * 100
                
                if outlier_pct > 10:  # More than 10% outliers
                    issue = QualityIssue(
                        column=col,
                        issue_type='accuracy',
                        severity='warning',
                        message=f"{len(outliers)} potential outliers ({outlier_pct:.2f}%)",
                        affected_rows=len(outliers),
                        affected_indices=outliers.index.tolist(),
                        suggestion=f"Review outliers in '{col}' for data accuracy"
                    )
                    
                    self.issues.append(issue)
        
        self.scores['accuracy'] = 100 - len([i for i in self.issues if i.issue_type == 'accuracy']) * 5
        self.scores['accuracy'] = max(0, self.scores['accuracy'])
    
    def _calculate_overall_score(self) -> float:
        """Kalkulasi overall quality score"""
        if not self.scores:
            return 0
        
        weights = {
            'completeness': 0.25,
            'uniqueness': 0.25,
            'consistency': 0.20,
            'validity': 0.20,
            'accuracy': 0.10
        }
        
        total_score = 0
        total_weight = 0
        
        for metric, weight in weights.items():
            if metric in self.scores:
                total_score += self.scores[metric] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Tentukan level kualitas berdasarkan score"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.FAIR
        elif score >= 40:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def _generate_recommendations(self) -> None:
        """Generate rekomendasi perbaikan"""
        self.recommendations = []
        
        # Group issues by type
        issues_by_type = {}
        for issue in self.issues:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = []
            issues_by_type[issue.issue_type].append(issue)
        
        # Generate recommendations based on issue types
        if 'completeness' in issues_by_type:
            self.recommendations.append(
                "Fill missing values or consider removing rows with critical missing data"
            )
        
        if 'uniqueness' in issues_by_type:
            self.recommendations.append(
                "Remove duplicate rows to ensure data uniqueness"
            )
        
        if 'consistency' in issues_by_type:
            self.recommendations.append(
                "Standardize formatting (case, whitespace) across all text columns"
            )
        
        if 'validity' in issues_by_type:
            self.recommendations.append(
                "Validate and correct data formats (phone numbers, dates, etc.)"
            )
        
        if 'accuracy' in issues_by_type:
            self.recommendations.append(
                "Review and verify outlier values for data accuracy"
            )
        
        # Add general recommendations
        if self.scores.get('completeness', 100) < 80:
            self.recommendations.append(
                "Focus on improving data completeness as it affects analysis quality"
            )
    
    def _issues_to_dict(self) -> List[Dict]:
        """Convert issues to dictionary"""
        return [
            {
                'column': issue.column,
                'issue_type': issue.issue_type,
                'severity': issue.severity,
                'message': issue.message,
                'affected_rows': issue.affected_rows,
                'suggestion': issue.suggestion
            }
            for issue in self.issues
        ]
    
    def get_issues_by_severity(self, severity: str) -> List[QualityIssue]:
        """
        Dapatkan issues berdasarkan severity
        
        Args:
            severity: Severity level (critical, warning, info)
            
        Returns:
            List issues
        """
        return [i for i in self.issues if i.severity == severity]
    
    def get_issues_by_column(self, column: str) -> List[QualityIssue]:
        """
        Dapatkan issues berdasarkan kolom
        
        Args:
            column: Nama kolom
            
        Returns:
            List issues
        """
        return [i for i in self.issues if i.column == column]
    
    def fix_common_issues(self) -> pd.DataFrame:
        """
        Perbaiki issue umum secara otomatis
        
        Returns:
            DataFrame yang sudah diperbaiki
        """
        df = self.df.copy()
        
        # Fix whitespace
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        
        # Fix phone numbers
        if 'Contact Number' in df.columns:
            df['Contact Number'] = df['Contact Number'].apply(
                lambda x: re.sub(r'\D', '', str(x)) if pd.notna(x) else x
            )
        
        # Remove exact duplicates
        df = df.drop_duplicates()
        
        logger.info(f"Fixed common issues. Rows before: {len(self.df)}, after: {len(df)}")
        
        return df


class QualityReport:
    """
    Generator untuk laporan kualitas data
    """
    
    def __init__(self, checker: DataQualityChecker):
        """
        Inisialisasi QualityReport
        
        Args:
            checker: Instance DataQualityChecker
        """
        self.checker = checker
    
    def generate_summary_card(self) -> Dict[str, Any]:
        """
        Generate summary card untuk UI
        
        Returns:
            Dictionary summary
        """
        result = self.checker.run_all_checks()
        
        # Determine color based on score
        score = result['overall_score']
        if score >= 80:
            color = '#00ff88'  # Green
            status = 'Excellent'
        elif score >= 60:
            color = '#ffaa00'  # Orange
            status = 'Good'
        else:
            color = '#ff4b4b'  # Red
            status = 'Needs Improvement'
        
        return {
            'score': score,
            'status': status,
            'color': color,
            'total_issues': result['total_issues'],
            'critical_issues': result['critical_issues'],
            'quality_level': result['quality_level']
        }
    
    def generate_detailed_report(self) -> str:
        """
        Generate laporan detail dalam format text
        
        Returns:
            String laporan
        """
        result = self.checker.run_all_checks()
        
        report = f"""
{'='*60}
DATA QUALITY REPORT
{'='*60}

Overall Score: {result['overall_score']:.2f}/100
Quality Level: {result['quality_level'].upper()}
Total Issues: {result['total_issues']}
  - Critical: {result['critical_issues']}
  - Warning: {result['warning_issues']}
  - Info: {result['info_issues']}

{'='*60}
DETAILED SCORES
{'='*60}
"""
        
        for metric, score in result['scores'].items():
            report += f"  {metric.capitalize():15s}: {score:.2f}/100\n"
        
        report += f"""
{'='*60}
ISSUES FOUND
{'='*60}
"""
        
        if result['issues']:
            for issue in result['issues']:
                report += f"""
[{issue['severity'].upper()}] {issue['issue_type'].upper()}
  Column: {issue['column']}
  Message: {issue['message']}
  Affected Rows: {issue['affected_rows']}
  Suggestion: {issue['suggestion']}
"""
        else:
            report += "\nNo issues found! Data quality is excellent.\n"
        
        report += f"""
{'='*60}
RECOMMENDATIONS
{'='*60}
"""
        
        if result['recommendations']:
            for i, rec in enumerate(result['recommendations'], 1):
                report += f"  {i}. {rec}\n"
        else:
            report += "\nNo recommendations needed.\n"
        
        report += f"\n{'='*60}\n"
        
        return report
