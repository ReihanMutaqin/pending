"""
Data Processor untuk WSA Fulfillment Pro
Berisi logika bisnis untuk memproses data WSA, MODOROSO, dan WAPPR
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

from config.settings import (
    COLUMN_MAPPINGS, FILTER_CONFIG, BULAN_SINGKAT
)
from src.utils import (
    logger, clean_string, parse_date, format_date,
    clean_dataframe, reorder_columns, normalize_phone,
    extract_order_id
)


class DataProcessor:
    """
    Kelas utama untuk memproses data WSA
    """
    
    def __init__(self, mode: str = "WSA"):
        """
        Inisialisasi DataProcessor
        
        Args:
            mode: Mode operasi (WSA, MODOROSO, WAPPR)
        """
        self.mode = mode.upper()
        self.col_sc = 'SC Order No/Track ID/CSRM No'
        self.df_raw = None
        self.df_processed = None
        self.df_final = None
        self.stats = {}
        
        logger.info(f"DataProcessor initialized with mode: {self.mode}")
    
    def load_data(self, df: pd.DataFrame) -> 'DataProcessor':
        """
        Load data mentah
        
        Args:
            df: DataFrame mentah
            
        Returns:
            Self untuk method chaining
        """
        self.df_raw = df.copy()
        self.stats['raw_rows'] = len(df)
        self.stats['raw_columns'] = len(df.columns)
        
        logger.info(f"Loaded {len(df)} rows with {len(df.columns)} columns")
        
        return self
    
    def clean_common(self) -> 'DataProcessor':
        """
        Bersihkan data dengan operasi umum
        
        Returns:
            Self untuk method chaining
        """
        if self.df_raw is None:
            raise ValueError("Data belum di-load. Panggil load_data() terlebih dahulu.")
        
        df = self.df_raw.copy()
        
        # Clean Workorder
        if 'Workorder' in df.columns:
            df['Workorder'] = df['Workorder'].apply(
                lambda x: clean_string(x).replace(r'\.0$', '', regex=True)
            )
        
        # Clean Booking Date
        if 'Booking Date' in df.columns:
            df['Booking Date'] = df['Booking Date'].astype(str).str.split('.').str[0]
        
        # Parse Date Created
        if 'Date Created' in df.columns:
            df['Date Created DT'] = df['Date Created'].apply(parse_date)
            df['Date Created Display'] = df['Date Created DT'].apply(
                lambda x: format_date(x, '%d/%m/%Y %H:%M') if x else ''
            )
        
        # Clean Contact Number
        if 'Contact Number' in df.columns:
            df['Contact Number'] = df['Contact Number'].apply(normalize_phone)
        
        # Clean SC Order No
        if self.col_sc in df.columns:
            df[self.col_sc] = df[self.col_sc].apply(
                lambda x: extract_order_id(clean_string(x))
            )
        
        self.df_processed = df
        self.stats['cleaned_rows'] = len(df)
        
        logger.info(f"Common cleaning completed. Rows: {len(df)}")
        
        return self
    
    def filter_by_mode(self) -> 'DataProcessor':
        """
        Filter data berdasarkan mode
        
        Returns:
            Self untuk method chaining
        """
        if self.df_processed is None:
            raise ValueError("Data belum di-clean. Panggil clean_common() terlebih dahulu.")
        
        df = self.df_processed.copy()
        
        if self.mode == "WSA":
            df = self._filter_wsa(df)
        elif self.mode == "MODOROSO":
            df = self._filter_modoroso(df)
        elif self.mode == "WAPPR":
            df = self._filter_wappr(df)
        
        self.df_processed = df
        self.stats['filtered_rows'] = len(df)
        
        logger.info(f"Mode filtering completed. Rows: {len(df)}")
        
        return self
    
    def _filter_wsa(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter untuk mode WSA
        
        Args:
            df: DataFrame input
            
        Returns:
            DataFrame yang sudah difilter
        """
        config = FILTER_CONFIG['WSA']
        
        # Filter by pattern
        if self.col_sc in df.columns:
            pattern = '|'.join(config['patterns'])
            df = df[df[self.col_sc].astype(str).str.contains(pattern, na=False, case=False)]
        
        # Filter by CRM Order Type
        if 'CRM Order Type' in df.columns:
            df = df[df['CRM Order Type'].isin(config['crm_order_types'])]
        
        # Fill Contact Number dari mapping Customer Name
        if 'Contact Number' in df.columns and 'Customer Name' in df.columns:
            df = self._fill_contact_number(df)
        
        return df
    
    def _filter_modoroso(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter untuk mode MODOROSO
        
        Args:
            df: DataFrame input
            
        Returns:
            DataFrame yang sudah difilter
        """
        config = FILTER_CONFIG['MODOROSO']
        
        # Filter by pattern
        if self.col_sc in df.columns:
            pattern = '|'.join(config['patterns'])
            df = df[df[self.col_sc].astype(str).str.contains(
                pattern, na=False, case=config.get('case_sensitive', False)
            )].copy()
        
        # Detect MO/DO type
        if 'CRM Order Type' in df.columns:
            df['CRM Order Type'] = df[self.col_sc].apply(self._detect_mo_do)
        
        # Set Mitra
        df['Mitra'] = config.get('default_mitra', 'TSEL')
        
        return df
    
    def _filter_wappr(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter untuk mode WAPPR
        
        Args:
            df: DataFrame input
            
        Returns:
            DataFrame yang sudah difilter
        """
        config = FILTER_CONFIG['WAPPR']
        
        # Filter by pattern
        if self.col_sc in df.columns:
            pattern = '|'.join(config['patterns'])
            df = df[df[self.col_sc].astype(str).str.contains(pattern, na=False, case=False)]
        
        # Filter by Status
        if 'Status' in df.columns:
            df = df[df['Status'].astype(str).str.strip().str.upper().isin(
                [s.upper() for s in config['status_filter']]
            )]
        
        return df
    
    def _detect_mo_do(self, val: str) -> str:
        """
        Deteksi tipe MO atau DO
        
        Args:
            val: Nilai yang akan dideteksi
            
        Returns:
            'MO' atau 'DO'
        """
        s = clean_string(val, uppercase=True)
        if '-MO' in s:
            return 'MO'
        if '-DO' in s:
            return 'DO'
        return 'MO'  # Default
    
    def _fill_contact_number(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Isi Contact Number yang kosong dari mapping Customer Name
        
        Args:
            df: DataFrame input
            
        Returns:
            DataFrame dengan Contact Number yang sudah diisi
        """
        # Buat mapping Customer Name -> Contact Number
        c_map = df.loc[
            df['Contact Number'].notna() & (df['Contact Number'] != ''),
            ['Customer Name', 'Contact Number']
        ].drop_duplicates('Customer Name')
        
        c_dict = dict(zip(c_map['Customer Name'], c_map['Contact Number']))
        
        # Fill missing Contact Number
        def fill_contact(row):
            val = str(row['Contact Number'])
            if pd.isna(row['Contact Number']) or val.strip() == '' or val.lower() == 'nan':
                return c_dict.get(row['Customer Name'], row['Contact Number'])
            return row['Contact Number']
        
        df['Contact Number'] = df.apply(fill_contact, axis=1)
        
        return df
    
    def filter_by_month(self, months: List[int]) -> 'DataProcessor':
        """
        Filter data berdasarkan bulan
        
        Args:
            months: List bulan (1-12)
            
        Returns:
            Self untuk method chaining
        """
        if self.df_processed is None:
            raise ValueError("Data belum di-filter. Panggil filter_by_mode() terlebih dahulu.")
        
        if not months:
            logger.warning("No months selected, skipping month filter")
            return self
        
        if 'Date Created DT' not in self.df_processed.columns:
            logger.warning("Date Created DT column not found, skipping month filter")
            return self
        
        df = self.df_processed.copy()
        before_count = len(df)
        
        df = df[df['Date Created DT'].dt.month.isin(months)]
        
        after_count = len(df)
        self.stats['month_filtered_rows'] = after_count
        self.stats['month_filtered_out'] = before_count - after_count
        
        self.df_processed = df
        
        logger.info(f"Month filter completed. Rows: {after_count} (filtered out: {before_count - after_count})")
        
        return self
    
    def remove_duplicates(self, existing_ids: List[str], check_col: str = None) -> 'DataProcessor':
        """
        Hapus data yang sudah ada di Google Sheets
        
        Args:
            existing_ids: List ID yang sudah ada
            check_col: Kolom untuk pengecekan duplikat
            
        Returns:
            Self untuk method chaining
        """
        if self.df_processed is None:
            raise ValueError("Data belum di-filter. Panggil filter_by_mode() terlebih dahulu.")
        
        if check_col is None:
            check_col = self.col_sc if self.mode in ['WSA', 'WAPPR'] else 'Workorder'
        
        if check_col not in self.df_processed.columns:
            logger.warning(f"Check column {check_col} not found, skipping duplicate removal")
            self.df_final = self.df_processed.copy()
            return self
        
        df = self.df_processed.copy()
        before_count = len(df)
        
        # Clean existing IDs
        existing_ids = [clean_string(str(x)) for x in existing_ids]
        
        # Remove duplicates
        df['__check_val'] = df[check_col].astype(str).str.strip()
        df = df[~df['__check_val'].isin(existing_ids)].copy()
        df = df.drop(columns=['__check_val'])
        
        after_count = len(df)
        self.stats['unique_rows'] = after_count
        self.stats['duplicates_removed'] = before_count - after_count
        
        self.df_final = df
        
        logger.info(f"Duplicate removal completed. Unique rows: {after_count} (removed: {before_count - after_count})")
        
        return self
    
    def finalize(self, sort_by: str = 'Workzone') -> pd.DataFrame:
        """
        Finalisasi data untuk output
        
        Args:
            sort_by: Kolom untuk sorting
            
        Returns:
            DataFrame final
        """
        if self.df_final is None:
            raise ValueError("Data belum di-proses. Panggil method processing terlebih dahulu.")
        
        df = self.df_final.copy()
        
        # Reorder columns
        target_order = COLUMN_MAPPINGS['output_columns'].get(self.mode, [])
        df = reorder_columns(df, target_order)
        
        # Update Date Created dengan format display
        if 'Date Created Display' in df.columns:
            df['Date Created'] = df['Date Created Display']
        
        # Drop temporary columns
        temp_cols = ['Date Created DT', 'Date Created Display', '__check_val']
        df = df.drop(columns=[c for c in temp_cols if c in df.columns], errors='ignore')
        
        # Sort
        if sort_by in df.columns:
            df = df.sort_values(sort_by)
        
        self.df_final = df
        self.stats['final_rows'] = len(df)
        
        logger.info(f"Finalization completed. Final rows: {len(df)}")
        
        return df
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Dapatkan statistik processing
        
        Returns:
            Dictionary statistik
        """
        return self.stats
    
    def process_all(self, df: pd.DataFrame, months: List[int] = None, 
                    existing_ids: List[str] = None) -> pd.DataFrame:
        """
        Jalankan semua proses dalam satu method
        
        Args:
            df: DataFrame mentah
            months: List bulan untuk filter
            existing_ids: List ID yang sudah ada
            
        Returns:
            DataFrame final
        """
        return (self
                .load_data(df)
                .clean_common()
                .filter_by_mode()
                .filter_by_month(months or [])
                .remove_duplicates(existing_ids or [])
                .finalize())


class BatchProcessor:
    """
    Processor untuk batch processing
    """
    
    def __init__(self, processor: DataProcessor, batch_size: int = 1000):
        """
        Inisialisasi BatchProcessor
        
        Args:
            processor: Instance DataProcessor
            batch_size: Ukuran batch
        """
        self.processor = processor
        self.batch_size = batch_size
        self.results = []
        self.errors = []
    
    def process_chunks(self, df: pd.DataFrame, **kwargs) -> List[pd.DataFrame]:
        """
        Proses data dalam chunk
        
        Args:
            df: DataFrame input
            **kwargs: Parameter untuk DataProcessor
            
        Returns:
            List DataFrame hasil
        """
        total_rows = len(df)
        num_chunks = (total_rows + self.batch_size - 1) // self.batch_size
        
        logger.info(f"Processing {total_rows} rows in {num_chunks} chunks")
        
        results = []
        
        for i in range(num_chunks):
            start_idx = i * self.batch_size
            end_idx = min((i + 1) * self.batch_size, total_rows)
            
            chunk = df.iloc[start_idx:end_idx]
            
            try:
                result = self.processor.process_all(chunk, **kwargs)
                results.append(result)
                logger.info(f"Chunk {i+1}/{num_chunks} processed: {len(result)} rows")
            except Exception as e:
                logger.error(f"Error processing chunk {i+1}/{num_chunks}: {e}")
                self.errors.append({
                    'chunk': i + 1,
                    'error': str(e),
                    'rows': len(chunk)
                })
        
        self.results = results
        
        if results:
            return pd.concat(results, ignore_index=True)
        
        return pd.DataFrame()
    
    def get_errors(self) -> List[Dict]:
        """
        Dapatkan list error
        
        Returns:
            List error
        """
        return self.errors
