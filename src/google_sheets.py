"""
Google Sheets Integration untuk WSA Fulfillment Pro
Berisi fungsi-fungsi untuk berinteraksi dengan Google Sheets API
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from config.settings import GOOGLE_SHEET_CONFIG
from src.utils import logger, clean_string


class GoogleSheetsManager:
    """
    Manager untuk operasi Google Sheets
    """
    
    def __init__(self, credentials: Dict = None):
        """
        Inisialisasi GoogleSheetsManager
        
        Args:
            credentials: Dictionary credentials service account (opsional)
        """
        self.credentials = credentials
        self.client = None
        self.spreadsheet = None
        self.worksheets = {}
        self.connection_status = False
        
        logger.info("GoogleSheetsManager initialized")
    
    def connect(self, credentials: Dict = None) -> bool:
        """
        Hubungkan ke Google Sheets API
        
        Args:
            credentials: Dictionary credentials (opsional, override constructor)
            
        Returns:
            True jika berhasil
        """
        creds = credentials or self.credentials
        
        if not creds:
            logger.error("No credentials provided")
            return False
        
        try:
            # Fix private key format
            info = dict(creds)
            if 'private_key' in info:
                info['private_key'] = info['private_key'].replace('\\n', '\n')
            
            # Create credentials
            scope = GOOGLE_SHEET_CONFIG['scope']
            credentials_obj = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
            
            # Authorize
            self.client = gspread.authorize(credentials_obj)
            self.connection_status = True
            
            logger.info("Successfully connected to Google Sheets API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets API: {e}")
            self.connection_status = False
            return False
    
    def open_spreadsheet(self, spreadsheet_name: str = None) -> bool:
        """
        Buka spreadsheet
        
        Args:
            spreadsheet_name: Nama spreadsheet (default dari config)
            
        Returns:
            True jika berhasil
        """
        if not self.connection_status:
            logger.error("Not connected to Google Sheets API")
            return False
        
        name = spreadsheet_name or GOOGLE_SHEET_CONFIG['spreadsheet_name']
        
        try:
            self.spreadsheet = self.client.open(name)
            logger.info(f"Opened spreadsheet: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to open spreadsheet '{name}': {e}")
            return False
    
    def get_worksheet(self, worksheet_name: str = None, index: int = None) -> Optional[gspread.Worksheet]:
        """
        Ambil worksheet
        
        Args:
            worksheet_name: Nama worksheet
            index: Index worksheet (alternatif)
            
        Returns:
            Worksheet object atau None
        """
        if not self.spreadsheet:
            logger.error("Spreadsheet not opened")
            return None
        
        try:
            if worksheet_name:
                ws = self.spreadsheet.worksheet(worksheet_name)
                self.worksheets[worksheet_name] = ws
                return ws
            elif index is not None:
                ws = self.spreadsheet.get_worksheet(index)
                if ws:
                    self.worksheets[ws.title] = ws
                return ws
            else:
                # Default to first worksheet
                ws = self.spreadsheet.get_worksheet(0)
                if ws:
                    self.worksheets[ws.title] = ws
                return ws
                
        except Exception as e:
            logger.error(f"Failed to get worksheet: {e}")
            return None
    
    def get_all_worksheets(self) -> List[str]:
        """
        Ambil semua nama worksheet
        
        Returns:
            List nama worksheet
        """
        if not self.spreadsheet:
            logger.error("Spreadsheet not opened")
            return []
        
        try:
            worksheets = self.spreadsheet.worksheets()
            return [ws.title for ws in worksheets]
            
        except Exception as e:
            logger.error(f"Failed to get worksheets: {e}")
            return []
    
    def read_data(self, worksheet_name: str = None, index: int = None) -> pd.DataFrame:
        """
        Baca data dari worksheet
        
        Args:
            worksheet_name: Nama worksheet
            index: Index worksheet (alternatif)
            
        Returns:
            DataFrame dengan data
        """
        ws = self.get_worksheet(worksheet_name, index)
        
        if not ws:
            logger.error("Worksheet not found")
            return pd.DataFrame()
        
        try:
            data = ws.get_all_records()
            df = pd.DataFrame(data)
            
            logger.info(f"Read {len(df)} rows from worksheet '{ws.title}'")
            return df
            
        except Exception as e:
            logger.error(f"Failed to read data: {e}")
            return pd.DataFrame()
    
    def get_existing_ids(self, worksheet_name: str = None, column: str = None, 
                         index: int = None) -> List[str]:
        """
        Ambil list ID yang sudah ada di worksheet
        
        Args:
            worksheet_name: Nama worksheet
            column: Nama kolom untuk ambil ID
            index: Index worksheet (alternatif)
            
        Returns:
            List ID yang sudah ada
        """
        df = self.read_data(worksheet_name, index)
        
        if df.empty:
            return []
        
        if column and column in df.columns:
            ids = df[column].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().unique()
        else:
            # Default to first column
            ids = df.iloc[:, 0].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().unique()
        
        logger.info(f"Found {len(ids)} existing IDs")
        return list(ids)
    
    def append_data(self, df: pd.DataFrame, worksheet_name: str = None, 
                    index: int = None, clear_first: bool = False) -> bool:
        """
        Tambah data ke worksheet
        
        Args:
            df: DataFrame yang akan ditambahkan
            worksheet_name: Nama worksheet
            index: Index worksheet (alternatif)
            clear_first: Hapus data existing terlebih dahulu
            
        Returns:
            True jika berhasil
        """
        ws = self.get_worksheet(worksheet_name, index)
        
        if not ws:
            logger.error("Worksheet not found")
            return False
        
        try:
            if clear_first:
                ws.clear()
            
            # Convert DataFrame to list of lists
            values = [df.columns.tolist()] + df.values.tolist()
            
            # Append data
            ws.append_rows(values[1:])  # Skip header if not clearing
            
            logger.info(f"Appended {len(df)} rows to worksheet '{ws.title}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to append data: {e}")
            return False
    
    def update_data(self, df: pd.DataFrame, worksheet_name: str = None, 
                    index: int = None) -> bool:
        """
        Update seluruh data worksheet
        
        Args:
            df: DataFrame yang akan diupdate
            worksheet_name: Nama worksheet
            index: Index worksheet (alternatif)
            
        Returns:
            True jika berhasil
        """
        ws = self.get_worksheet(worksheet_name, index)
        
        if not ws:
            logger.error("Worksheet not found")
            return False
        
        try:
            # Clear existing data
            ws.clear()
            
            # Convert DataFrame to list of lists
            values = [df.columns.tolist()] + df.values.tolist()
            
            # Update data
            ws.update(values)
            
            logger.info(f"Updated {len(df)} rows in worksheet '{ws.title}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update data: {e}")
            return False
    
    def log_activity(self, activity: Dict[str, Any], worksheet_name: str = "ACTIVITY_LOG") -> bool:
        """
        Log aktivitas ke worksheet
        
        Args:
            activity: Dictionary aktivitas
            worksheet_name: Nama worksheet log
            
        Returns:
            True jika berhasil
        """
        try:
            # Try to get or create log worksheet
            try:
                ws = self.spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                ws = self.spreadsheet.add_worksheet(worksheet_name, rows=1000, cols=10)
                # Add header
                ws.append_row(['Timestamp', 'User', 'Action', 'Mode', 'Rows', 'Status', 'Message'])
            
            # Prepare log entry
            log_entry = [
                datetime.now().isoformat(),
                activity.get('user', 'system'),
                activity.get('action', 'unknown'),
                activity.get('mode', ''),
                activity.get('rows', 0),
                activity.get('status', 'success'),
                activity.get('message', '')
            ]
            
            ws.append_row(log_entry)
            
            logger.info(f"Logged activity: {activity.get('action')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            return False
    
    def backup_data(self, worksheet_name: str = None, backup_name: str = None) -> bool:
        """
        Backup data worksheet
        
        Args:
            worksheet_name: Nama worksheet yang akan di-backup
            backup_name: Nama worksheet backup
            
        Returns:
            True jika berhasil
        """
        if not worksheet_name:
            logger.error("Worksheet name required for backup")
            return False
        
        try:
            # Read source data
            df = self.read_data(worksheet_name)
            
            if df.empty:
                logger.warning(f"No data to backup from '{worksheet_name}'")
                return False
            
            # Generate backup name
            if not backup_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"BACKUP_{worksheet_name}_{timestamp}"
            
            # Create or get backup worksheet
            try:
                ws = self.spreadsheet.worksheet(backup_name)
                ws.clear()
            except gspread.WorksheetNotFound:
                ws = self.spreadsheet.add_worksheet(backup_name, rows=len(df)+10, cols=len(df.columns)+2)
            
            # Write backup data
            values = [df.columns.tolist()] + df.values.tolist()
            ws.update(values)
            
            logger.info(f"Backed up '{worksheet_name}' to '{backup_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup data: {e}")
            return False
    
    def get_sheet_info(self) -> Dict[str, Any]:
        """
        Dapatkan informasi spreadsheet
        
        Returns:
            Dictionary informasi
        """
        if not self.spreadsheet:
            logger.error("Spreadsheet not opened")
            return {}
        
        try:
            worksheets = self.spreadsheet.worksheets()
            
            info = {
                'title': self.spreadsheet.title,
                'url': self.spreadsheet.url,
                'worksheets': [
                    {
                        'title': ws.title,
                        'rows': ws.row_count,
                        'cols': ws.col_count
                    }
                    for ws in worksheets
                ]
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get sheet info: {e}")
            return {}
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test koneksi ke Google Sheets
        
        Returns:
            Tuple (success, message)
        """
        if not self.client:
            return False, "Not connected to Google Sheets API"
        
        try:
            # Try to list spreadsheets
            spreadsheets = self.client.list_spreadsheet_files()
            return True, f"Connected. Found {len(spreadsheets)} spreadsheets."
            
        except Exception as e:
            return False, f"Connection test failed: {e}"


class StreamlitGoogleSheets:
    """
    Wrapper untuk Google Sheets di Streamlit dengan caching
    """
    
    def __init__(self):
        self.manager = None
        self._cache = {}
    
    def connect_with_secrets(self) -> bool:
        """
        Hubungkan menggunakan Streamlit secrets
        
        Returns:
            True jika berhasil
        """
        try:
            import streamlit as st
            
            credentials = dict(st.secrets["gcp_service_account"])
            
            self.manager = GoogleSheetsManager(credentials)
            return self.manager.connect()
            
        except Exception as e:
            logger.error(f"Failed to connect with secrets: {e}")
            return False
    
    def get_cached_data(self, worksheet_name: str, cache_ttl: int = 300) -> pd.DataFrame:
        """
        Ambil data dengan caching
        
        Args:
            worksheet_name: Nama worksheet
            cache_ttl: Time to live cache (detik)
            
        Returns:
            DataFrame dengan data
        """
        import time
        
        cache_key = f"gsheet_{worksheet_name}"
        
        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if time.time() - cached_time < cache_ttl:
                logger.info(f"Returning cached data for '{worksheet_name}'")
                return cached_data
        
        # Fetch fresh data
        if not self.manager:
            logger.error("Not connected")
            return pd.DataFrame()
        
        df = self.manager.read_data(worksheet_name)
        
        # Update cache
        self._cache[cache_key] = (df, time.time())
        
        return df
    
    def clear_cache(self, worksheet_name: str = None):
        """
        Clear cache
        
        Args:
            worksheet_name: Nama worksheet (None = clear all)
        """
        if worksheet_name:
            cache_key = f"gsheet_{worksheet_name}"
            self._cache.pop(cache_key, None)
        else:
            self._cache.clear()
        
        logger.info("Cache cleared")


# Helper function untuk Streamlit
def get_gspread_client_streamlit():
    """
    Get gspread client untuk Streamlit dengan caching
    
    Returns:
        GoogleSheetsManager instance atau None
    """
    try:
        import streamlit as st
        
        @st.cache_resource
        def _get_client():
            try:
                info = dict(st.secrets["gcp_service_account"])
                if 'private_key' in info:
                    info['private_key'] = info['private_key'].replace('\\n', '\n')
                
                scope = GOOGLE_SHEET_CONFIG['scope']
                creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
                client = gspread.authorize(creds)
                
                return client
                
            except Exception as e:
                logger.error(f"Failed to create client: {e}")
                return None
        
        client = _get_client()
        
        if client:
            manager = GoogleSheetsManager()
            manager.client = client
            manager.connection_status = True
            return manager
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get client: {e}")
        return None
