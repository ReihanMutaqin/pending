"""
Konfigurasi Aplikasi WSA Fulfillment Pro
File ini berisi semua pengaturan dan konfigurasi aplikasi
"""

import os
from datetime import datetime

# ==========================================
# KONFIGURASI APLIKASI
# ==========================================
APP_NAME = "WSA Fulfillment Pro"
APP_VERSION = "2.0.0"
APP_AUTHOR = "WSA Team"
APP_DESCRIPTION = "Sistem Manajemen Data WSA dengan Integrasi Google Sheets"

# ==========================================
# KONFIGURASI GOOGLE SHEETS
# ==========================================
GOOGLE_SHEET_CONFIG = {
    "spreadsheet_name": "Salinan dari NEW GDOC WSA FULFILLMENT",
    "worksheets": {
        "WSA": "Sheet1",
        "MODOROSO": "MODOROSO_JAKTIMSEL",
        "WAPPR": "WAPPR_DATA",
        "LOG": "ACTIVITY_LOG",
        "BACKUP": "BACKUP_DATA"
    },
    "scope": [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
}

# ==========================================
# KONFIGURASI KOLOM DATA
# ==========================================
COLUMN_MAPPINGS = {
    "required_columns": [
        "SC Order No/Track ID/CSRM No",
        "Workorder",
        "Date Created",
        "Service No.",
        "Status"
    ],
    "optional_columns": [
        "CRM Order Type",
        "Address",
        "Customer Name",
        "Workzone",
        "Booking Date",
        "Contact Number",
        "Mitra"
    ],
    "output_columns": {
        "WSA": [
            "Date Created", "Workorder", "SC Order No/Track ID/CSRM No",
            "Service No.", "CRM Order Type", "Status", "Address",
            "Customer Name", "Workzone", "Booking Date", "Contact Number"
        ],
        "MODOROSO": [
            "Date Created", "Workorder", "SC Order No/Track ID/CSRM No",
            "Service No.", "CRM Order Type", "Status", "Address",
            "Customer Name", "Workzone", "Contact Number", "Mitra"
        ],
        "WAPPR": [
            "Date Created", "Workorder", "SC Order No/Track ID/CSRM No",
            "Service No.", "CRM Order Type", "Status", "Address",
            "Customer Name", "Workzone", "Booking Date", "Contact Number"
        ]
    }
}

# ==========================================
# KONFIGURASI FILTER
# ==========================================
FILTER_CONFIG = {
    "WSA": {
        "patterns": ["AO", "PDA", "WSA"],
        "crm_order_types": ["CREATE", "MIGRATE"],
        "status_include": [],
        "status_exclude": []
    },
    "MODOROSO": {
        "patterns": [r"-MO", r"-DO"],
        "case_sensitive": False,
        "default_mitra": "TSEL"
    },
    "WAPPR": {
        "patterns": ["AO", "PDA"],
        "status_filter": ["WAPPR"]
    }
}

# ==========================================
# KONFIGURASI LOGGING
# ==========================================
LOG_CONFIG = {
    "enabled": True,
    "log_dir": "logs",
    "log_file": f"wsa_app_{datetime.now().strftime('%Y%m%d')}.log",
    "max_file_size": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5,
    "log_level": "INFO",
    "console_output": True
}

# ==========================================
# KONFIGURASI UI
# ==========================================
UI_CONFIG = {
    "theme": "dark",
    "primary_color": "#00d4ff",
    "secondary_color": "#008fb3",
    "success_color": "#00ff88",
    "error_color": "#ff4b4b",
    "warning_color": "#ffaa00",
    "page_title": "WSA Fulfillment Pro",
    "page_icon": "🚀",
    "layout": "wide"
}

# ==========================================
# KONFIGURASI EXPORT
# ==========================================
EXPORT_CONFIG = {
    "formats": ["xlsx", "csv", "json"],
    "default_format": "xlsx",
    "excel_engine": "xlsxwriter",
    "csv_encoding": "utf-8-sig",
    "date_format": "%d%m%Y",
    "filename_prefix": "WSA_Cleaned"
}

# ==========================================
# KONFIGURASI DATA QUALITY
# ==========================================
QUALITY_CONFIG = {
    "check_nulls": True,
    "check_duplicates": True,
    "check_format": True,
    "null_threshold": 0.1,  # 10% null = warning
    "duplicate_threshold": 0.05,  # 5% duplicate = warning
    "validate_phone": True,
    "validate_dates": True
}

# ==========================================
# KONFIGURASI CACHE
# ==========================================
CACHE_CONFIG = {
    "ttl": 3600,  # 1 jam
    "max_entries": 100
}

# ==========================================
# BULAN INDONESIA
# ==========================================
BULAN_INDONESIA = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

BULAN_SINGKAT = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu",
    9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"
}

# ==========================================
# PESAN ERROR
# ==========================================
ERROR_MESSAGES = {
    "no_file": "⚠️ Silakan upload file terlebih dahulu",
    "invalid_format": "❌ Format file tidak didukung. Gunakan XLSX, XLS, atau CSV",
    "no_connection": "❌ Gagal terhubung ke Google Sheets. Periksa koneksi dan credentials",
    "sheet_not_found": "❌ Sheet tidak ditemukan. Periksa nama sheet",
    "empty_data": "⚠️ Tidak ada data yang memenuhi kriteria filter",
    "processing_error": "❌ Terjadi kesalahan saat memproses data",
    "export_error": "❌ Gagal mengekspor data"
}

# ==========================================
# PESAN SUKSES
# ==========================================
SUCCESS_MESSAGES = {
    "connected": "✅ Berhasil terhubung ke Google Sheets",
    "processed": "✅ Data berhasil diproses",
    "exported": "✅ Data berhasil diekspor",
    "uploaded": "✅ File berhasil diupload"
}
