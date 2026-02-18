"""
Utility Functions untuk WSA Fulfillment Pro
Berisi helper functions yang digunakan di seluruh aplikasi
"""

import os
import re
import io
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np

from config.settings import (
    LOG_CONFIG, BULAN_INDONESIA, BULAN_SINGKAT,
    ERROR_MESSAGES, SUCCESS_MESSAGES, EXPORT_CONFIG
)


# ==========================================
# LOGGER SETUP
# ==========================================
def setup_logger(name: str = "WSA_APP") -> logging.Logger:
    """
    Setup logger dengan konfigurasi yang fleksibel
    
    Args:
        name: Nama logger
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_CONFIG["log_level"]))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File Handler
    if LOG_CONFIG["enabled"]:
        log_dir = LOG_CONFIG["log_dir"]
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, LOG_CONFIG["log_file"])
        
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=LOG_CONFIG["max_file_size"],
            backupCount=LOG_CONFIG["backup_count"],
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Console Handler
    if LOG_CONFIG["console_output"]:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger()


# ==========================================
# DATE & TIME UTILITIES
# ==========================================
def parse_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
    """
    Parse tanggal dari berbagai format
    
    Args:
        date_str: String tanggal
        formats: List format yang didukung
        
    Returns:
        datetime object atau None
    """
    if formats is None:
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%m/%d/%Y %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y'
        ]
    
    if pd.isna(date_str) or str(date_str).strip() == '':
        return None
    
    date_str = str(date_str).strip()
    
    # Remove .0 suffix
    date_str = re.sub(r'\.0$', '', date_str)
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def format_date(date_obj: datetime, format_str: str = '%d/%m/%Y %H:%M') -> str:
    """
    Format datetime ke string
    
    Args:
        date_obj: datetime object
        format_str: Format output
        
    Returns:
        Formatted date string
    """
    if date_obj is None or pd.isna(date_obj):
        return ''
    return date_obj.strftime(format_str)


def get_bulan_indonesia(month_num: int, singkat: bool = False) -> str:
    """
    Konversi nomor bulan ke nama bulan Indonesia
    
    Args:
        month_num: Nomor bulan (1-12)
        singkat: Gunakan singkatan
        
    Returns:
        Nama bulan
    """
    if singkat:
        return BULAN_SINGKAT.get(month_num, 'Unknown')
    return BULAN_INDONESIA.get(month_num, 'Unknown')


def get_current_period() -> Tuple[int, int]:
    """
    Dapatkan periode bulan saat ini dan sebelumnya
    
    Returns:
        Tuple (bulan_sekarang, bulan_sebelumnya)
    """
    curr_month = datetime.now().month
    prev_month = curr_month - 1 if curr_month > 1 else 12
    return curr_month, prev_month


# ==========================================
# STRING UTILITIES
# ==========================================
def clean_string(val: Any, uppercase: bool = False, strip: bool = True) -> str:
    """
    Bersihkan dan normalisasi string
    
    Args:
        val: Value yang akan dibersihkan
        uppercase: Konversi ke uppercase
        strip: Hapus whitespace di awal/akhir
        
    Returns:
        String yang sudah dibersihkan
    """
    if pd.isna(val):
        return ''
    
    result = str(val)
    
    if strip:
        result = result.strip()
    
    # Remove .0 suffix for numbers
    result = re.sub(r'\.0$', '', result)
    
    if uppercase:
        result = result.upper()
    
    return result


def normalize_phone(phone: str) -> str:
    """
    Normalisasi nomor telepon
    
    Args:
        phone: Nomor telepon
        
    Returns:
        Nomor telepon yang sudah dinormalisasi
    """
    if pd.isna(phone) or str(phone).strip() == '':
        return ''
    
    phone = clean_string(phone)
    
    # Remove non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # Format Indonesia
    if phone.startswith('0'):
        phone = '62' + phone[1:]
    elif phone.startswith('8'):
        phone = '62' + phone
    
    return phone


def validate_phone(phone: str) -> bool:
    """
    Validasi format nomor telepon Indonesia
    
    Args:
        phone: Nomor telepon
        
    Returns:
        True jika valid
    """
    phone = normalize_phone(phone)
    
    # Minimal 10 digit, maksimal 15 digit
    if len(phone) < 10 or len(phone) > 15:
        return False
    
    # Harus dimulai dengan 62
    if not phone.startswith('62'):
        return False
    
    return True


def extract_order_id(text: str) -> str:
    """
    Extract order ID dari string
    
    Args:
        text: String yang mengandung order ID
        
    Returns:
        Order ID yang sudah dibersihkan
    """
    text = clean_string(text)
    
    # Remove suffix after underscore
    if '_' in text:
        text = text.split('_')[0]
    
    return text


# ==========================================
# DATAFRAME UTILITIES
# ==========================================
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bersihkan dataframe dari nilai-nilai tidak valid
    
    Args:
        df: DataFrame input
        
    Returns:
        DataFrame yang sudah dibersihkan
    """
    df = df.copy()
    
    # Replace common null values
    null_values = ['', 'nan', 'NaN', 'NULL', 'null', 'None', 'none', '-']
    df = df.replace(null_values, np.nan)
    
    # Clean string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: clean_string(x))
    
    return df


def safe_convert_numeric(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Konversi kolom ke numeric dengan aman
    
    Args:
        df: DataFrame input
        columns: List kolom yang akan dikonversi
        
    Returns:
        DataFrame dengan kolom yang sudah dikonversi
    """
    df = df.copy()
    
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def reorder_columns(df: pd.DataFrame, target_order: List[str]) -> pd.DataFrame:
    """
    Reorder kolom dataframe sesuai target
    
    Args:
        df: DataFrame input
        target_order: List urutan kolom yang diinginkan
        
    Returns:
        DataFrame dengan kolom yang sudah di-reorder
    """
    existing_cols = [c for c in target_order if c in df.columns]
    remaining_cols = [c for c in df.columns if c not in target_order]
    
    return df[existing_cols + remaining_cols]


def get_column_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Dapatkan statistik kolom dataframe
    
    Args:
        df: DataFrame input
        
    Returns:
        Dictionary statistik
    """
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'null_counts': df.isnull().sum().to_dict(),
        'null_percentages': (df.isnull().sum() / len(df) * 100).to_dict()
    }
    
    return stats


# ==========================================
# EXPORT UTILITIES
# ==========================================
def export_to_excel(df: pd.DataFrame, filename: str = None) -> bytes:
    """
    Export dataframe ke Excel
    
    Args:
        df: DataFrame yang akan diexport
        filename: Nama file (opsional)
        
    Returns:
        Bytes data Excel
    """
    if filename is None:
        filename = f"{EXPORT_CONFIG['filename_prefix']}_{datetime.now().strftime(EXPORT_CONFIG['date_format'])}.xlsx"
    
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine=EXPORT_CONFIG['excel_engine']) as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Data']
        for i, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max(),
                len(str(col))
            ) + 2
            worksheet.set_column(i, i, min(max_length, 50))
    
    return buffer.getvalue()


def export_to_csv(df: pd.DataFrame, filename: str = None) -> bytes:
    """
    Export dataframe ke CSV
    
    Args:
        df: DataFrame yang akan diexport
        filename: Nama file (opsional)
        
    Returns:
        Bytes data CSV
    """
    if filename is None:
        filename = f"{EXPORT_CONFIG['filename_prefix']}_{datetime.now().strftime(EXPORT_CONFIG['date_format'])}.csv"
    
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding=EXPORT_CONFIG['csv_encoding'])
    
    return buffer.getvalue().encode(EXPORT_CONFIG['csv_encoding'])


def export_to_json(df: pd.DataFrame, filename: str = None) -> bytes:
    """
    Export dataframe ke JSON
    
    Args:
        df: DataFrame yang akan diexport
        filename: Nama file (opsional)
        
    Returns:
        Bytes data JSON
    """
    if filename is None:
        filename = f"{EXPORT_CONFIG['filename_prefix']}_{datetime.now().strftime(EXPORT_CONFIG['date_format'])}.json"
    
    json_str = df.to_json(orient='records', date_format='iso')
    
    return json_str.encode('utf-8')


# ==========================================
# VALIDATION UTILITIES
# ==========================================
def validate_file_extension(filename: str, allowed_extensions: List[str] = None) -> bool:
    """
    Validasi ekstensi file
    
    Args:
        filename: Nama file
        allowed_extensions: List ekstensi yang diizinkan
        
    Returns:
        True jika valid
    """
    if allowed_extensions is None:
        allowed_extensions = ['.xlsx', '.xls', '.csv']
    
    ext = os.path.splitext(filename.lower())[1]
    return ext in allowed_extensions


def validate_required_columns(df: pd.DataFrame, required_cols: List[str]) -> Tuple[bool, List[str]]:
    """
    Validasi keberadaan kolom yang diperlukan
    
    Args:
        df: DataFrame input
        required_cols: List kolom yang diperlukan
        
    Returns:
        Tuple (is_valid, missing_columns)
    """
    missing = [col for col in required_cols if col not in df.columns]
    return len(missing) == 0, missing


# ==========================================
# SECURITY UTILITIES
# ==========================================
def generate_hash(data: str) -> str:
    """
    Generate hash dari string
    
    Args:
        data: String yang akan di-hash
        
    Returns:
        Hash string
    """
    return hashlib.sha256(data.encode()).hexdigest()


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Masking data sensitif
    
    Args:
        data: Data yang akan di-mask
        visible_chars: Jumlah karakter yang tetap terlihat
        
    Returns:
        Data yang sudah di-mask
    """
    if len(data) <= visible_chars:
        return '*' * len(data)
    
    return data[:visible_chars] + '*' * (len(data) - visible_chars)


# ==========================================
# PERFORMANCE UTILITIES
# ==========================================
def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Bagi list menjadi chunk
    
    Args:
        lst: List yang akan di-chunk
        chunk_size: Ukuran setiap chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def memory_usage(df: pd.DataFrame) -> str:
    """
    Dapatkan penggunaan memory dataframe
    
    Args:
        df: DataFrame input
        
    Returns:
        String penggunaan memory
    """
    mem = df.memory_usage(deep=True).sum()
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if mem < 1024:
            return f"{mem:.2f} {unit}"
        mem /= 1024
    
    return f"{mem:.2f} TB"


# ==========================================
# NOTIFICATION UTILITIES
# ==========================================
def create_notification(message: str, type_: str = 'info') -> Dict[str, str]:
    """
    Buat notifikasi
    
    Args:
        message: Pesan notifikasi
        type_: Tipe notifikasi (info, success, warning, error)
        
    Returns:
        Dictionary notifikasi
    """
    icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    return {
        'message': message,
        'type': type_,
        'icon': icons.get(type_, 'ℹ️'),
        'timestamp': datetime.now().isoformat()
    }


# ==========================================
# SESSION STATE UTILITIES (for Streamlit)
# ==========================================
def init_session_state(keys: Dict[str, Any]) -> None:
    """
    Inisialisasi session state Streamlit
    
    Args:
        keys: Dictionary key-value untuk session state
    """
    import streamlit as st
    
    for key, value in keys.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_session_state(key: str, default: Any = None) -> Any:
    """
    Ambil nilai dari session state
    
    Args:
        key: Key session state
        default: Nilai default jika key tidak ada
        
    Returns:
        Nilai session state
    """
    import streamlit as st
    
    return st.session_state.get(key, default)


def set_session_state(key: str, value: Any) -> None:
    """
    Set nilai session state
    
    Args:
        key: Key session state
        value: Nilai yang akan diset
    """
    import streamlit as st
    
    st.session_state[key] = value
