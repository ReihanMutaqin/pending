# 🚀 WSA Fulfillment Pro

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/yourusername/wsa-fulfillment)
[![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Aplikasi manajemen data WSA (Work Service Assurance) dengan integrasi Google Sheets yang powerful dan mudah digunakan.

![WSA Fulfillment Pro Screenshot](docs/screenshot.png)

## ✨ Fitur Utama

### 📊 Multi-Mode Processing
- **WSA (Validation)**: Validasi data WSA dengan filter otomatis
- **MODOROSO**: Proses data MO/DO dengan deteksi otomatis
- **WAPPR**: Filter data berdasarkan status WAPPR

### 🔍 Data Quality Checker
- Pengecekan kelengkapan data (null values)
- Deteksi duplikat
- Validasi format (nomor telepon, tanggal)
- Score kualitas data real-time
- Rekomendasi perbaikan otomatis

### 📈 Analytics Dashboard
- Analisis berdasarkan status
- Analisis berdasarkan workzone
- Analisis tren bulanan
- Top customers
- Visualisasi data interaktif

### 💾 Multi-Format Export
- Excel (.xlsx) dengan formatting otomatis
- CSV (.csv) dengan encoding UTF-8
- JSON (.json) untuk integrasi API

### 🔐 Integrasi Google Sheets
- Koneksi aman via Service Account
- Validasi duplikat real-time
- Auto-backup data
- Activity logging

## 🚀 Quick Start

### Prerequisites

- Python 3.8 atau lebih tinggi
- Google Cloud Project dengan Google Sheets API enabled
- Service Account credentials

### Installation

1. **Clone repository**
```bash
git clone https://github.com/yourusername/wsa-fulfillment.git
cd wsa-fulfillment
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup Google Sheets Credentials**
   - Buat project di [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google Sheets API dan Google Drive API
   - Buat Service Account dan download credentials JSON
   - Rename file menjadi `credentials.json` dan simpan di folder `config/`

4. **Konfigurasi Streamlit Secrets**

Buat file `.streamlit/secrets.toml`:
```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

5. **Run aplikasi**
```bash
streamlit run app.py
```

## 📁 Struktur Project

```
wsa_fulfillment/
├── app.py                      # Aplikasi utama Streamlit
├── config/
│   ├── __init__.py
│   └── settings.py             # Konfigurasi aplikasi
├── src/
│   ├── __init__.py
│   ├── utils.py                # Utility functions
│   ├── data_processor.py       # Logika bisnis processing
│   ├── google_sheets.py        # Integrasi Google Sheets
│   ├── analytics.py            # Analytics dan reporting
│   └── quality_checker.py      # Data quality checker
├── tests/
│   ├── __init__.py
│   ├── test_utils.py
│   ├── test_data_processor.py
│   └── test_quality_checker.py
├── logs/                       # Log files
├── docs/                       # Dokumentasi
├── requirements.txt
└── README.md
```

## 📖 Usage Guide

### 1. Pilih Mode Operasi

Di sidebar, pilih salah satu mode:
- **WSA (Validation)**: Untuk validasi data WSA
- **MODOROSO**: Untuk proses data MO/DO
- **WAPPR**: Untuk filter data WAPPR

### 2. Filter Periode

Pilih bulan yang ingin difilter (default: bulan ini dan bulan lalu)

### 3. Upload File

Upload file data Anda dalam format:
- Excel (.xlsx, .xls)
- CSV (.csv)

### 4. Proses Data

Sistem akan otomatis:
1. Membaca dan membersihkan data
2. Memfilter berdasarkan mode
3. Memfilter berdasarkan bulan
4. Mengecek duplikat dengan Google Sheets
5. Menghasilkan data final

### 5. Review Analytics

Lihat analytics dashboard untuk:
- Statistik data
- Distribusi status
- Analisis workzone
- Top customers

### 6. Quality Check

Periksa kualitas data dengan:
- Quality score
- Daftar issues
- Rekomendasi perbaikan

### 7. Export Data

Download hasil dalam format:
- Excel (.xlsx)
- CSV (.csv)
- JSON (.json)

## ⚙️ Konfigurasi

### Settings (`config/settings.py`)

```python
# Konfigurasi Google Sheets
GOOGLE_SHEET_CONFIG = {
    "spreadsheet_name": "Your Spreadsheet Name",
    "worksheets": {
        "WSA": "Sheet1",
        "MODOROSO": "MODOROSO_DATA",
        "WAPPR": "WAPPR_DATA"
    }
}

# Konfigurasi Filter
FILTER_CONFIG = {
    "WSA": {
        "patterns": ["AO", "PDA", "WSA"],
        "crm_order_types": ["CREATE", "MIGRATE"]
    },
    "MODOROSO": {
        "patterns": [r"-MO", r"-DO"],
        "default_mitra": "TSEL"
    },
    "WAPPR": {
        "patterns": ["AO", "PDA"],
        "status_filter": ["WAPPR"]
    }
}

# Konfigurasi Export
EXPORT_CONFIG = {
    "formats": ["xlsx", "csv", "json"],
    "default_format": "xlsx",
    "filename_prefix": "WSA_Cleaned"
}
```

## 🧪 Testing

Jalankan unit tests:

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_utils
python -m unittest tests.test_data_processor
python -m unittest tests.test_quality_checker

# Run with verbose output
python -m unittest discover tests/ -v
```

## 📊 Data Quality Metrics

Aplikasi ini menggunakan 5 metrik utama untuk menilai kualitas data:

| Metrik | Bobot | Deskripsi |
|--------|-------|-----------|
| Completeness | 25% | Persentase data lengkap (non-null) |
| Uniqueness | 25% | Persentase data unik (non-duplicate) |
| Consistency | 20% | Konsistensi format data |
| Validity | 20% | Validitas format (phone, date, dll) |
| Accuracy | 10% | Akurasi data (outlier detection) |

### Quality Levels

| Score | Level | Status |
|-------|-------|--------|
| 90-100 | Excellent | 🟢 |
| 75-89 | Good | 🟢 |
| 60-74 | Fair | 🟡 |
| 40-59 | Poor | 🟠 |
| 0-39 | Critical | 🔴 |

## 🔧 Advanced Usage

### Custom Data Processor

```python
from src.data_processor import DataProcessor

# Buat processor custom
processor = DataProcessor(mode='WSA')

# Process dengan parameter kustom
df_final = (processor
    .load_data(df_raw)
    .clean_common()
    .filter_by_mode()
    .filter_by_month([1, 2, 3])
    .remove_duplicates(existing_ids)
    .finalize(sort_by='Customer Name'))

# Get stats
stats = processor.get_stats()
print(f"Input: {stats['raw_rows']}, Output: {stats['final_rows']}")
```

### Batch Processing

```python
from src.data_processor import DataProcessor, BatchProcessor

# Batch processing untuk data besar
processor = DataProcessor(mode='WSA')
batch_processor = BatchProcessor(processor, batch_size=1000)

result = batch_processor.process_chunks(
    large_df,
    months=[1, 2],
    existing_ids=[]
)

# Check errors
errors = batch_processor.get_errors()
```

### Quality Check

```python
from src.quality_checker import DataQualityChecker, QualityReport

# Check quality
checker = DataQualityChecker(df)
report = QualityReport(checker)

# Get summary
summary = report.generate_summary_card()
print(f"Quality Score: {summary['score']}")
print(f"Status: {summary['status']}")

# Get detailed report
print(report.generate_detailed_report())

# Fix common issues
fixed_df = checker.fix_common_issues()
```

### Analytics

```python
from src.analytics import DataAnalyzer, ReportGenerator

# Analyze data
analyzer = DataAnalyzer(df)

# Get various analyses
status_analysis = analyzer.analyze_by_status()
workzone_analysis = analyzer.analyze_by_workzone()
month_analysis = analyzer.analyze_by_month()
top_customers = analyzer.get_top_customers(top_n=10)

# Generate full report
report = analyzer.generate_full_report()

# Generate HTML report
generator = ReportGenerator(analyzer)
html_report = generator.generate_html_report()
```

## 📝 Logging

Log file tersimpan di folder `logs/` dengan format:

```
logs/
├── wsa_app_20240115.log
├── wsa_app_20240116.log
└── ...
```

Konfigurasi logging di `config/settings.py`:

```python
LOG_CONFIG = {
    "enabled": True,
    "log_dir": "logs",
    "log_level": "INFO",
    "max_file_size": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5
}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Google Sheets Connection Failed

**Error**: `Failed to connect to Google Sheets API`

**Solution**:
- Pastikan credentials JSON valid
- Periksa Service Account memiliki akses ke spreadsheet
- Enable Google Sheets API dan Google Drive API di Google Cloud Console

#### 2. Sheet Not Found

**Error**: `Sheet 'XXX' tidak ditemukan`

**Solution**:
- Periksa nama sheet di Google Sheets
- Update `GOOGLE_SHEET_CONFIG` di `config/settings.py`

#### 3. Invalid File Format

**Error**: `Format file tidak didukung`

**Solution**:
- Pastikan file berformat .xlsx, .xls, atau .csv
- Periksa file tidak corrupt

#### 4. Memory Error

**Error**: `MemoryError` saat processing data besar

**Solution**:
- Gunakan BatchProcessor untuk data besar
- Kurangi batch_size jika diperlukan
- Tutup aplikasi lain yang tidak diperlukan

## 🤝 Contributing

Kontribusi sangat diterima! Silakan ikuti langkah berikut:

1. Fork repository
2. Buat branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👥 Team

- **Lead Developer**: WSA Team
- **Contributors**: [List contributors]

## 📞 Support

Untuk pertanyaan dan support:
- Email: support@wsa-team.com
- Issue Tracker: [GitHub Issues](https://github.com/yourusername/wsa-fulfillment/issues)

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - Framework UI
- [Google Sheets API](https://developers.google.com/sheets/api) - Data integration
- [Pandas](https://pandas.pydata.org/) - Data processing
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Excel handling

---

<p align="center">
  Made with ❤️ by WSA Team
</p>
