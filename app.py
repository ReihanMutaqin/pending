"""
WSA Fulfillment Pro - Aplikasi Utama
Aplikasi Streamlit untuk manajemen data WSA dengan integrasi Google Sheets

Fitur:
- Multi-mode: WSA, MODOROSO, WAPPR
- Data cleansing dan validasi
- Integrasi Google Sheets
- Analytics dan reporting
- Data quality checker
- Multi-format export
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Import konfigurasi
from config.settings import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION,
    UI_CONFIG, BULAN_SINGKAT, ERROR_MESSAGES, SUCCESS_MESSAGES,
    EXPORT_CONFIG
)

# Import utilities
from src.utils import (
    logger, get_bulan_indonesia, get_current_period,
    validate_file_extension, memory_usage,
    export_to_excel, export_to_csv, export_to_json,
    init_session_state
)

# Import processors
from src.data_processor import DataProcessor
from src.google_sheets import get_gspread_client_streamlit
from src.analytics import DataAnalyzer, MetricsCalculator, ReportGenerator
from src.quality_checker import DataQualityChecker, QualityReport

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title=f"{APP_NAME} v{APP_VERSION}",
    page_icon=UI_CONFIG['page_icon'],
    layout=UI_CONFIG['layout'],
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS CUSTOM
# ==========================================
st.markdown(f"""
    <style>
    /* Main Theme */
    .stApp {{
        background-color: #0e1117;
        color: #ffffff;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #1a1c24;
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {UI_CONFIG['primary_color']} !important;
    }}
    
    /* Metric Cards */
    .metric-card {{
        background: linear-gradient(135deg, #1e2129 0%, #2a2d3a 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid {UI_CONFIG['primary_color']};
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.1);
        margin-bottom: 15px;
    }}
    
    .metric-card h2 {{
        margin: 0;
        font-size: 32px;
        color: {UI_CONFIG['primary_color']} !important;
    }}
    
    .metric-card h5 {{
        margin: 0;
        color: #888;
        font-size: 12px;
        text-transform: uppercase;
    }}
    
    /* Status Boxes */
    .status-box {{
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-weight: 600;
    }}
    
    .success-box {{
        background: linear-gradient(135deg, #1c4f2e 0%, #2d6a4f 100%);
        color: {UI_CONFIG['success_color']};
        border: 1px solid {UI_CONFIG['success_color']};
    }}
    
    .error-box {{
        background: linear-gradient(135deg, #4f1c1c 0%, #6a2d2d 100%);
        color: {UI_CONFIG['error_color']};
        border: 1px solid {UI_CONFIG['error_color']};
    }}
    
    .warning-box {{
        background: linear-gradient(135deg, #4f3c1c 0%, #6a5d2d 100%);
        color: {UI_CONFIG['warning_color']};
        border: 1px solid {UI_CONFIG['warning_color']};
    }}
    
    /* Download Buttons */
    .stDownloadButton button {{
        background: linear-gradient(45deg, {UI_CONFIG['primary_color']}, {UI_CONFIG['secondary_color']}) !important;
        color: #000000 !important;
        font-weight: bold;
        width: 100%;
        border-radius: 10px;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }}
    
    .stDownloadButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: #1e2129;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #888;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {UI_CONFIG['primary_color']} !important;
        color: #000 !important;
    }}
    
    /* DataFrame */
    .stDataFrame {{
        border-radius: 10px;
        overflow: hidden;
    }}
    
    /* Progress Bar */
    .stProgress > div > div {{
        background-color: {UI_CONFIG['primary_color']};
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: #1e2129;
        border-radius: 8px;
    }}
    
    /* Info Box */
    .info-box {{
        background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid {UI_CONFIG['primary_color']};
        margin-bottom: 15px;
    }}
    
    /* Quality Score */
    .quality-score {{
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 50%;
        width: 120px;
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
    }}
    
    /* Animation */
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    
    .pulse {{
        animation: pulse 2s infinite;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
init_session_state({
    'processed_data': None,
    'raw_data': None,
    'analytics_report': None,
    'quality_report': None,
    'processing_stats': {},
    'last_upload': None,
    'connection_status': False
})

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.title(f"⚙️ {APP_NAME}")
    st.caption(f"v{APP_VERSION}")
    st.markdown("---")
    
    # Mode Selection
    st.subheader("📋 Mode Operasi")
    menu = st.radio(
        "Pilih Mode:",
        ["WSA (Validation)", "MODOROSO", "WAPPR"],
        help="Pilih mode operasi sesuai kebutuhan"
    )
    
    st.markdown("---")
    
    # Filter Bulan
    st.subheader("📅 Filter Periode")
    curr_month, prev_month = get_current_period()
    
    selected_months = st.multiselect(
        "Bulan:",
        options=list(range(1, 13)),
        default=[prev_month, curr_month],
        format_func=lambda x: get_bulan_indonesia(x, singkat=True)
    )
    
    st.markdown("---")
    
    # Settings
    st.subheader("🔧 Pengaturan")
    
    show_preview = st.checkbox("Tampilkan Preview Data", value=True)
    show_analytics = st.checkbox("Tampilkan Analytics", value=True)
    show_quality = st.checkbox("Data Quality Check", value=True)
    
    st.markdown("---")
    
    # Info
    st.info(f"""
    **{APP_NAME}**
    
    {APP_DESCRIPTION}
    
    **Fitur:**
    - ✅ Data Cleansing
    - ✅ Validasi Duplikat
    - ✅ Analytics Dashboard
    - ✅ Quality Checker
    - ✅ Multi-format Export
    """)

# ==========================================
# MAIN CONTENT
# ==========================================
st.title(f"🚀 {menu}")
st.caption(f"{APP_NAME} - {datetime.now().strftime('%d %B %Y')}")

# ==========================================
# KONEKSI GOOGLE SHEETS
# ==========================================
@st.cache_resource(show_spinner=False)
def get_gs_client():
    """Get Google Sheets client dengan caching"""
    return get_gspread_client_streamlit()

gs_client = get_gs_client()

if gs_client:
    # Open spreadsheet
    spreadsheet_opened = gs_client.open_spreadsheet()
    
    if spreadsheet_opened:
        st.session_state.connection_status = True
        
        # Get worksheet berdasarkan mode
        if menu == "MODOROSO":
            ws = gs_client.get_worksheet("MODOROSO_JAKTIMSEL")
            target_sheet_name = "MODOROSO_JAKTIMSEL"
        else:
            ws = gs_client.get_worksheet(index=0)
            target_sheet_name = ws.title if ws else "Unknown"
        
        if ws:
            st.markdown(
                f'<div class="status-box success-box">'
                f'✅ TERHUBUNG KE GOOGLE SHEETS | Sheet: {target_sheet_name}'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="status-box warning-box">'
                f'⚠️ TERHUBUNG TAPI SHEET TIDAK DITEMUKAN'
                f'</div>',
                unsafe_allow_html=True
            )
    else:
        st.session_state.connection_status = False
        st.markdown(
            f'<div class="status-box error-box">'
            f'❌ GAGAL MEMBUKA SPREADSHEET'
            f'</div>',
            unsafe_allow_html=True
        )
else:
    st.session_state.connection_status = False
    st.markdown(
        f'<div class="status-box error-box">'
        f'❌ GAGAL TERHUBUNG KE GOOGLE SHEETS - PERIKSA SECRETS'
        f'</div>',
        unsafe_allow_html=True
    )

# ==========================================
# FILE UPLOAD
# ==========================================
st.markdown("---")
st.subheader("📤 Upload Data")

uploaded_file = st.file_uploader(
    f"Drop file {menu} (XLSX/CSV)",
    type=["xlsx", "xls", "csv"],
    help="Upload file data WSA, MODOROSO, atau WAPPR"
)

# ==========================================
# PROCESSING
# ==========================================
if uploaded_file:
    # Validasi file
    if not validate_file_extension(uploaded_file.name):
        st.error(ERROR_MESSAGES['invalid_format'])
    else:
        start_time = time.time()
        
        with st.spinner("Membaca file..."):
            try:
                # Baca file
                if uploaded_file.name.lower().endswith('.csv'):
                    df_raw = pd.read_csv(uploaded_file)
                else:
                    df_raw = pd.read_excel(uploaded_file)
                
                st.session_state.raw_data = df_raw
                st.session_state.last_upload = datetime.now()
                
                st.success(f"✅ File berhasil dibaca: {len(df_raw):,} baris, {len(df_raw.columns)} kolom")
                
            except Exception as e:
                st.error(f"❌ Gagal membaca file: {e}")
                st.stop()
        
        # Preview Data Mentah
        if show_preview:
            with st.expander("📋 Preview Data Mentah", expanded=False):
                st.dataframe(df_raw.head(100), use_container_width=True)
                st.caption(f"Menampilkan 100 dari {len(df_raw):,} baris | Memory: {memory_usage(df_raw)}")
        
        # Processing
        with st.spinner(f"Memproses data {menu}..."):
            try:
                # Get existing IDs dari Google Sheets
                existing_ids = []
                if gs_client and ws:
                    check_col = 'SC Order No/Track ID/CSRM No' if menu in ["WSA (Validation)", "WAPPR"] else 'Workorder'
                    existing_ids = gs_client.get_existing_ids(column=check_col)
                
                # Process data
                mode_map = {
                    "WSA (Validation)": "WSA",
                    "MODOROSO": "MODOROSO",
                    "WAPPR": "WAPPR"
                }
                
                processor = DataProcessor(mode=mode_map[menu])
                
                df_final = (processor
                    .load_data(df_raw)
                    .clean_common()
                    .filter_by_mode()
                    .filter_by_month(selected_months)
                    .remove_duplicates(existing_ids)
                    .finalize())
                
                st.session_state.processed_data = df_final
                st.session_state.processing_stats = processor.get_stats()
                
                processing_time = time.time() - start_time
                
            except Exception as e:
                st.error(f"❌ Gagal memproses data: {e}")
                logger.error(f"Processing error: {e}", exc_info=True)
                st.stop()
        
        # ==========================================
        # METRICS
        # ==========================================
        st.markdown("---")
        st.subheader("📊 Ringkasan Processing")
        
        stats = st.session_state.processing_stats
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                f'<div class="metric-card">'
                f'<h5>📂 Data Input</h5>'
                f'<h2>{stats.get("raw_rows", 0):,}</h2>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f'<div class="metric-card">'
                f'<h5>🔍 Data Filtered</h5>'
                f'<h2>{stats.get("filtered_rows", 0):,}</h2>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f'<div class="metric-card">'
                f'<h5>✨ Data Unik</h5>'
                f'<h2>{stats.get("unique_rows", 0):,}</h2>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                f'<div class="metric-card">'
                f'<h5>🎯 Data Final</h5>'
                f'<h2 style="color: #00ff88;">{len(df_final):,}</h2>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        # Processing details
        with st.expander("📈 Detail Processing", expanded=False):
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                st.write("**Statistik Processing:**")
                st.write(f"- Waktu processing: {processing_time:.2f} detik")
                st.write(f"- Data yang difilter bulan: {stats.get('month_filtered_out', 0):,}")
                st.write(f"- Duplikat dihapus: {stats.get('duplicates_removed', 0):,}")
            
            with detail_col2:
                st.write("**Kolom Output:**")
                st.write(", ".join(df_final.columns.tolist()))
        
        # ==========================================
        # DATA QUALITY CHECK
        # ==========================================
        if show_quality and len(df_final) > 0:
            st.markdown("---")
            st.subheader("🔍 Data Quality Check")
            
            quality_checker = DataQualityChecker(df_final)
            quality_report = QualityReport(quality_checker)
            summary_card = quality_report.generate_summary_card()
            
            st.session_state.quality_report = quality_report.generate_detailed_report()
            
            q_col1, q_col2, q_col3 = st.columns([1, 2, 1])
            
            with q_col2:
                score_color = summary_card['color']
                st.markdown(
                    f'<div style="text-align: center;">'
                    f'<div style="'
                    f'font-size: 72px; font-weight: bold; color: {score_color};'
                    f'">{summary_card["score"]}</div>'
                    f'<div style="font-size: 18px; color: #888;">Quality Score</div>'
                    f'<div style="font-size: 24px; color: {score_color}; margin-top: 10px;">'
                    f'{summary_card["status"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            # Quality metrics
            qm_col1, qm_col2, qm_col3, qm_col4 = st.columns(4)
            
            with qm_col1:
                st.metric("Total Issues", summary_card['total_issues'])
            with qm_col2:
                st.metric("Critical", summary_card['critical_issues'], delta_color="inverse")
            with qm_col3:
                st.metric("Warnings", summary_card['warning_issues'])
            with qm_col4:
                st.metric("Quality Level", summary_card['quality_level'].upper())
            
            # Detailed quality report
            with st.expander("📋 Laporan Quality Detail", expanded=False):
                st.text(st.session_state.quality_report)
        
        # ==========================================
        # ANALYTICS
        # ==========================================
        if show_analytics and len(df_final) > 0:
            st.markdown("---")
            st.subheader("📈 Analytics Dashboard")
            
            analyzer = DataAnalyzer(df_final)
            
            # Tabs untuk berbagai analisis
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Status", "🌍 Workzone", "📅 Bulan", "🏆 Top Customers"
            ])
            
            with tab1:
                status_analysis = analyzer.analyze_by_status()
                if not status_analysis.empty:
                    st.dataframe(status_analysis, use_container_width=True)
                    
                    # Bar chart
                    st.bar_chart(status_analysis.set_index('Status')['Count'])
                else:
                    st.info("Tidak ada data status untuk dianalisis")
            
            with tab2:
                workzone_analysis = analyzer.analyze_by_workzone()
                if not workzone_analysis.empty:
                    st.dataframe(workzone_analysis, use_container_width=True)
                else:
                    st.info("Tidak ada data workzone untuk dianalisis")
            
            with tab3:
                month_analysis = analyzer.analyze_by_month()
                if not month_analysis.empty:
                    st.dataframe(month_analysis, use_container_width=True)
                else:
                    st.info("Tidak ada data bulan untuk dianalisis")
            
            with tab4:
                top_customers = analyzer.get_top_customers(top_n=10)
                if not top_customers.empty:
                    st.dataframe(top_customers, use_container_width=True)
                else:
                    st.info("Tidak ada data customer untuk dianalisis")
        
        # ==========================================
        # PREVIEW & DOWNLOAD
        # ==========================================
        st.markdown("---")
        st.subheader("📋 Preview Data Final")
        
        st.dataframe(df_final, use_container_width=True, height=400)
        
        st.caption(f"Menampilkan {len(df_final):,} baris data | {len(df_final.columns)} kolom")
        
        # Download Section
        st.markdown("---")
        st.subheader("💾 Export Data")
        
        dl_col1, dl_col2, dl_col3 = st.columns(3)
        
        timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
        mode_short = menu.split()[0]
        
        with dl_col1:
            # Excel Export
            excel_data = export_to_excel(df_final)
            st.download_button(
                label="📥 Download Excel (.xlsx)",
                data=excel_data,
                file_name=f"{EXPORT_CONFIG['filename_prefix']}_{mode_short}_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with dl_col2:
            # CSV Export
            csv_data = export_to_csv(df_final)
            st.download_button(
                label="📥 Download CSV (.csv)",
                data=csv_data,
                file_name=f"{EXPORT_CONFIG['filename_prefix']}_{mode_short}_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with dl_col3:
            # JSON Export
            json_data = export_to_json(df_final)
            st.download_button(
                label="📥 Download JSON (.json)",
                data=json_data,
                file_name=f"{EXPORT_CONFIG['filename_prefix']}_{mode_short}_{timestamp}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Success message
        st.markdown("---")
        st.success(f"✅ Processing selesai! {len(df_final):,} data siap digunakan.")

else:
    # Empty state
    st.markdown("---")
    st.info("""
    👋 **Selamat Datang di WSA Fulfillment Pro!**
    
    Untuk memulai:
    1. Pilih mode operasi di sidebar (WSA/MODOROSO/WAPPR)
    2. Sesuaikan filter bulan jika diperlukan
    3. Upload file data Anda (XLSX/CSV)
    4. Sistem akan otomatis memproses dan membersihkan data
    5. Download hasil dalam format yang diinginkan
    
    **Tips:** Pastikan file memiliki kolom yang diperlukan seperti 
    'SC Order No/Track ID/CSRM No', 'Workorder', dan 'Date Created'
    """)

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption(f"© 2024 {APP_NAME} v{APP_VERSION} | Dibuat dengan ❤️ untuk WSA Team")
