"""
Analytics & Reporting untuk WSA Fulfillment Pro
Berisi fungsi-fungsi untuk analisis data dan pembuatan laporan
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter

from src.utils import logger, get_bulan_indonesia


class DataAnalyzer:
    """
    Kelas untuk analisis data WSA
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Inisialisasi DataAnalyzer
        
        Args:
            df: DataFrame yang akan dianalisis
        """
        self.df = df.copy()
        self.stats = {}
        
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate summary statistics
        
        Returns:
            Dictionary summary
        """
        summary = {
            'total_records': len(self.df),
            'total_columns': len(self.df.columns),
            'columns': list(self.df.columns),
            'memory_usage': self._calculate_memory(),
            'null_summary': self._null_summary(),
            'data_types': self._data_types_summary()
        }
        
        self.stats['summary'] = summary
        return summary
    
    def _calculate_memory(self) -> str:
        """Calculate memory usage"""
        mem = self.df.memory_usage(deep=True).sum()
        for unit in ['B', 'KB', 'MB', 'GB']:
            if mem < 1024:
                return f"{mem:.2f} {unit}"
            mem /= 1024
        return f"{mem:.2f} TB"
    
    def _null_summary(self) -> Dict[str, Any]:
        """Summary null values"""
        null_counts = self.df.isnull().sum()
        null_pcts = (null_counts / len(self.df) * 100).round(2)
        
        return {
            'total_nulls': int(null_counts.sum()),
            'columns_with_nulls': int((null_counts > 0).sum()),
            'null_percentages': null_pcts.to_dict(),
            'null_counts': null_counts.to_dict()
        }
    
    def _data_types_summary(self) -> Dict[str, str]:
        """Summary data types"""
        return {col: str(dtype) for col, dtype in self.df.dtypes.items()}
    
    def analyze_by_status(self, status_col: str = 'Status') -> pd.DataFrame:
        """
        Analisis berdasarkan status
        
        Args:
            status_col: Nama kolom status
            
        Returns:
            DataFrame analisis
        """
        if status_col not in self.df.columns:
            logger.warning(f"Status column '{status_col}' not found")
            return pd.DataFrame()
        
        analysis = self.df[status_col].value_counts().reset_index()
        analysis.columns = ['Status', 'Count']
        analysis['Percentage'] = (analysis['Count'] / len(self.df) * 100).round(2)
        
        return analysis
    
    def analyze_by_workzone(self, workzone_col: str = 'Workzone') -> pd.DataFrame:
        """
        Analisis berdasarkan workzone
        
        Args:
            workzone_col: Nama kolom workzone
            
        Returns:
            DataFrame analisis
        """
        if workzone_col not in self.df.columns:
            logger.warning(f"Workzone column '{workzone_col}' not found")
            return pd.DataFrame()
        
        analysis = self.df[workzone_col].value_counts().reset_index()
        analysis.columns = ['Workzone', 'Count']
        analysis['Percentage'] = (analysis['Count'] / len(self.df) * 100).round(2)
        
        return analysis
    
    def analyze_by_month(self, date_col: str = 'Date Created DT') -> pd.DataFrame:
        """
        Analisis berdasarkan bulan
        
        Args:
            date_col: Nama kolom tanggal
            
        Returns:
            DataFrame analisis
        """
        if date_col not in self.df.columns:
            logger.warning(f"Date column '{date_col}' not found")
            return pd.DataFrame()
        
        df_copy = self.df.copy()
        df_copy['Month'] = df_copy[date_col].dt.month
        df_copy['Month_Name'] = df_copy['Month'].apply(get_bulan_indonesia)
        
        analysis = df_copy.groupby(['Month', 'Month_Name']).size().reset_index(name='Count')
        analysis['Percentage'] = (analysis['Count'] / len(self.df) * 100).round(2)
        analysis = analysis.sort_values('Month')
        
        return analysis[['Month_Name', 'Count', 'Percentage']]
    
    def analyze_by_crm_type(self, crm_col: str = 'CRM Order Type') -> pd.DataFrame:
        """
        Analisis berdasarkan tipe CRM Order
        
        Args:
            crm_col: Nama kolom CRM Order Type
            
        Returns:
            DataFrame analisis
        """
        if crm_col not in self.df.columns:
            logger.warning(f"CRM Order Type column '{crm_col}' not found")
            return pd.DataFrame()
        
        analysis = self.df[crm_col].value_counts().reset_index()
        analysis.columns = ['CRM Order Type', 'Count']
        analysis['Percentage'] = (analysis['Count'] / len(self.df) * 100).round(2)
        
        return analysis
    
    def analyze_trends(self, date_col: str = 'Date Created DT') -> pd.DataFrame:
        """
        Analisis tren waktu
        
        Args:
            date_col: Nama kolom tanggal
            
        Returns:
            DataFrame tren
        """
        if date_col not in self.df.columns:
            logger.warning(f"Date column '{date_col}' not found")
            return pd.DataFrame()
        
        df_copy = self.df.copy()
        df_copy['Date'] = df_copy[date_col].dt.date
        
        trends = df_copy.groupby('Date').size().reset_index(name='Count')
        trends['Date'] = pd.to_datetime(trends['Date'])
        trends = trends.sort_values('Date')
        
        # Calculate moving average
        trends['MA_7'] = trends['Count'].rolling(window=7, min_periods=1).mean().round(2)
        
        return trends
    
    def get_top_customers(self, customer_col: str = 'Customer Name', 
                          top_n: int = 10) -> pd.DataFrame:
        """
        Dapatkan top customers
        
        Args:
            customer_col: Nama kolom customer
            top_n: Jumlah top customers
            
        Returns:
            DataFrame top customers
        """
        if customer_col not in self.df.columns:
            logger.warning(f"Customer column '{customer_col}' not found")
            return pd.DataFrame()
        
        top = self.df[customer_col].value_counts().head(top_n).reset_index()
        top.columns = ['Customer Name', 'Order Count']
        
        return top
    
    def generate_full_report(self) -> Dict[str, Any]:
        """
        Generate laporan lengkap
        
        Returns:
            Dictionary laporan lengkap
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.generate_summary(),
            'by_status': self.analyze_by_status().to_dict('records'),
            'by_workzone': self.analyze_by_workzone().to_dict('records'),
            'by_month': self.analyze_by_month().to_dict('records'),
            'by_crm_type': self.analyze_by_crm_type().to_dict('records'),
            'trends': self.analyze_trends().to_dict('records'),
            'top_customers': self.get_top_customers().to_dict('records')
        }
        
        return report


class MetricsCalculator:
    """
    Kalkulator untuk berbagai metrik
    """
    
    def __init__(self, df_before: pd.DataFrame = None, df_after: pd.DataFrame = None):
        """
        Inisialisasi MetricsCalculator
        
        Args:
            df_before: DataFrame sebelum processing
            df_after: DataFrame setelah processing
        """
        self.df_before = df_before
        self.df_after = df_after
    
    def calculate_processing_metrics(self) -> Dict[str, Any]:
        """
        Kalkulasi metrik processing
        
        Returns:
            Dictionary metrik
        """
        if self.df_before is None or self.df_after is None:
            return {}
        
        before_count = len(self.df_before)
        after_count = len(self.df_after)
        
        metrics = {
            'input_records': before_count,
            'output_records': after_count,
            'records_filtered': before_count - after_count,
            'filter_rate': round((before_count - after_count) / before_count * 100, 2) if before_count > 0 else 0,
            'retention_rate': round(after_count / before_count * 100, 2) if before_count > 0 else 0
        }
        
        return metrics
    
    def calculate_quality_score(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Kalkulasi quality score
        
        Args:
            df: DataFrame yang akan dihitung (default: df_after)
            
        Returns:
            Dictionary quality score
        """
        df = df or self.df_after
        
        if df is None or df.empty:
            return {'overall_score': 0, 'details': {}}
        
        total_cells = df.size
        null_cells = df.isnull().sum().sum()
        null_rate = null_cells / total_cells if total_cells > 0 else 0
        
        # Calculate completeness score
        completeness = (1 - null_rate) * 100
        
        # Calculate uniqueness score (check duplicates)
        if len(df) > 0:
            duplicate_rate = df.duplicated().sum() / len(df)
            uniqueness = (1 - duplicate_rate) * 100
        else:
            uniqueness = 100
        
        # Overall score (weighted average)
        overall = (completeness * 0.6 + uniqueness * 0.4)
        
        return {
            'overall_score': round(overall, 2),
            'completeness': round(completeness, 2),
            'uniqueness': round(uniqueness, 2),
            'null_count': int(null_cells),
            'null_rate': round(null_rate * 100, 2),
            'duplicate_count': int(df.duplicated().sum())
        }
    
    def calculate_efficiency_metrics(self, processing_time: float, 
                                     records_processed: int) -> Dict[str, Any]:
        """
        Kalkulasi metrik efisiensi
        
        Args:
            processing_time: Waktu processing (detik)
            records_processed: Jumlah record yang diproses
            
        Returns:
            Dictionary metrik efisiensi
        """
        if processing_time <= 0:
            return {}
        
        return {
            'processing_time_seconds': round(processing_time, 2),
            'processing_time_formatted': self._format_duration(processing_time),
            'records_per_second': round(records_processed / processing_time, 2),
            'records_processed': records_processed
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format durasi ke string"""
        if seconds < 60:
            return f"{seconds:.2f} detik"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes} menit {secs} detik"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours} jam {minutes} menit"


class ReportGenerator:
    """
    Generator untuk berbagai jenis laporan
    """
    
    def __init__(self, analyzer: DataAnalyzer = None):
        """
        Inisialisasi ReportGenerator
        
        Args:
            analyzer: Instance DataAnalyzer
        """
        self.analyzer = analyzer
    
    def generate_html_report(self, title: str = "WSA Analytics Report") -> str:
        """
        Generate laporan dalam format HTML
        
        Args:
            title: Judul laporan
            
        Returns:
            String HTML
        """
        if not self.analyzer:
            return "<p>No analyzer provided</p>"
        
        report = self.analyzer.generate_full_report()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                h1 {{ color: #00d4ff; }}
                h2 {{ color: #333; border-bottom: 2px solid #00d4ff; padding-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; text-align: left; border: 1px solid #ddd; }}
                th {{ background: #00d4ff; color: white; }}
                tr:nth-child(even) {{ background: #f9f9f9; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f0f0f0; border-radius: 5px; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #00d4ff; }}
                .metric-label {{ font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                <p>Generated at: {report['generated_at']}</p>
                
                <h2>Summary</h2>
                <div class="metric">
                    <div class="metric-value">{report['summary']['total_records']:,}</div>
                    <div class="metric-label">Total Records</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{report['summary']['total_columns']}</div>
                    <div class="metric-label">Total Columns</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{report['summary']['memory_usage']}</div>
                    <div class="metric-label">Memory Usage</div>
                </div>
                
                <h2>By Status</h2>
                {self._dict_to_html_table(report['by_status'])}
                
                <h2>By Workzone</h2>
                {self._dict_to_html_table(report['by_workzone'])}
                
                <h2>By Month</h2>
                {self._dict_to_html_table(report['by_month'])}
                
                <h2>Top Customers</h2>
                {self._dict_to_html_table(report['top_customers'])}
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _dict_to_html_table(self, data: List[Dict]) -> str:
        """Convert list of dict to HTML table"""
        if not data:
            return "<p>No data available</p>"
        
        headers = list(data[0].keys())
        
        html = "<table><thead><tr>"
        for header in headers:
            html += f"<th>{header}</th>"
        html += "</tr></thead><tbody>"
        
        for row in data:
            html += "<tr>"
            for header in headers:
                value = row.get(header, '')
                if isinstance(value, float):
                    value = f"{value:.2f}"
                html += f"<td>{value}</td>"
            html += "</tr>"
        
        html += "</tbody></table>"
        
        return html
    
    def generate_markdown_report(self, title: str = "WSA Analytics Report") -> str:
        """
        Generate laporan dalam format Markdown
        
        Args:
            title: Judul laporan
            
        Returns:
            String Markdown
        """
        if not self.analyzer:
            return "No analyzer provided"
        
        report = self.analyzer.generate_full_report()
        
        md = f"""# {title}

**Generated at:** {report['generated_at']}

## Summary

- **Total Records:** {report['summary']['total_records']:,}
- **Total Columns:** {report['summary']['total_columns']}
- **Memory Usage:** {report['summary']['memory_usage']}

## By Status

| Status | Count | Percentage |
|--------|-------|------------|
"""
        
        for item in report['by_status']:
            md += f"| {item.get('Status', 'N/A')} | {item.get('Count', 0):,} | {item.get('Percentage', 0):.2f}% |\n"
        
        md += """
## By Workzone

| Workzone | Count | Percentage |
|----------|-------|------------|
"""
        
        for item in report['by_workzone']:
            md += f"| {item.get('Workzone', 'N/A')} | {item.get('Count', 0):,} | {item.get('Percentage', 0):.2f}% |\n"
        
        md += """
## Top Customers

| Customer Name | Order Count |
|---------------|-------------|
"""
        
        for item in report['top_customers']:
            md += f"| {item.get('Customer Name', 'N/A')} | {item.get('Order Count', 0):,} |\n"
        
        return md
