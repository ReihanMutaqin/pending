import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io
from datetime import datetime
import time

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="WSA Fulfillment Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS MODERN & PROFESIONAL
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1320 50%, #0a0e1a 100%);
        color: #e8ecf1;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1623 0%, #151d2e 100%);
        border-right: 1px solid rgba(0, 212, 255, 0.1);
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        padding: 8px;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: #94a3b8 !important;
        font-weight: 500;
        padding: 10px 15px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(0, 212, 255, 0.1);
        color: #00d4ff !important;
    }
    
    [data-testid="stSidebar"] [aria-checked="true"] {
        background: linear-gradient(135deg, #00d4ff 0%, #008fb3 100%) !important;
        color: #000 !important;
        font-weight: 600 !important;
    }
    
    /* Headers */
    h1 {
        background: linear-gradient(90deg, #00d4ff 0%, #00ff88 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2, h3 {
        color: #00d4ff !important;
        font-weight: 600 !important;
    }
    
    /* Status Box */
    .status-box {
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 24px;
        font-weight: 600;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        backdrop-filter: blur(10px);
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.15) 0%, rgba(0, 255, 136, 0.05) 100%);
        border: 1px solid rgba(0, 255, 136, 0.3);
        color: #00ff88;
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(255, 75, 75, 0.15) 0%, rgba(255, 75, 75, 0.05) 100%);
        border: 1px solid rgba(255, 75, 75, 0.3);
        color: #ff4b4b;
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(255, 170, 0, 0.15) 0%, rgba(255, 170, 0, 0.05) 100%);
        border: 1px solid rgba(255, 170, 0, 0.3);
        color: #ffaa00;
    }
    
    /* Metric Cards */
    .metric-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(0, 212, 255, 0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00d4ff, #00ff88);
    }
    
    .metric-container:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 212, 255, 0.15);
        border-color: rgba(0, 212, 255, 0.3);
    }
    
    .metric-icon {
        font-size: 28px;
        margin-bottom: 12px;
    }
    
    .metric-value {
        font-size: 42px;
        font-weight: 700;
        background: linear-gradient(90deg, #fff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
    }
    
    .metric-value.success {
        background: linear-gradient(90deg, #00ff88 0%, #00cc6a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 8px;
    }
    
    /* Upload Area */
    .upload-area {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%);
        border: 2px dashed rgba(0, 212, 255, 0.3);
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #00d4ff;
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%);
    }
    
    /* DataFrame */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(0, 212, 255, 0.1);
    }
    
    /* Download Button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #00d4ff 0%, #008fb3 100%) !important;
        color: #000 !important;
        font-weight: 600 !important;
        padding: 14px 28px !important;
        border-radius: 12px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        font-size: 14px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stDownloadButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.4) !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00d4ff 0%, #00ff88 100%) !important;
        border-radius: 10px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        border-radius: 12px;
        border: 1px solid rgba(0, 212, 255, 0.1);
        font-weight: 500;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #00d4ff !important;
        border-top-color: transparent !important;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(0, 212, 255, 0.3) 50%, transparent 100%);
        margin: 30px 0;
    }
    
    /* Caption */
    .stCaption {
        color: #64748b !important;
    }
    
    /* Multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, #00d4ff 0%, #008fb3 100%) !important;
        color: #000 !important;
    }
    
    /* File Uploader */
    .stFileUploader {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(0, 212, 255, 0.1);
    }
    
    /* Animation */
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.2); }
        50% { box-shadow: 0 0 40px rgba(0, 212, 255, 0.4); }
    }
    
    .glow-effect {
        animation: pulse-glow 2s infinite;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0e1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00d4ff 0%, #008fb3 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00ff88 0%, #00cc6a 100%);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# KONEKSI GOOGLE SHEETS
# ==========================================
@st.cache_resource(show_spinner=False)
def get_gspread_client():
    try:
        info = dict(st.secrets["gcp_service_account"])
        if 'private_key' in info:
            info['private_key'] = info['private_key'].replace('\\n', '\n')
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds)
    except Exception as e:
        return None

# ==========================================
# FUNGSI LOGIKA
# ==========================================
def clean_common_data(df):
    if 'Workorder' in df.columns:
        df['Workorder'] = df['Workorder'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    if 'Booking Date' in df.columns:
        df['Booking Date'] = df['Booking Date'].astype(str).str.split('.').str[0]
    return df

def proses_wsa(df):
    col_sc = 'SC Order No/Track ID/CSRM No'
    df = df[df[col_sc].astype(str).str.contains('AO|PDA|WSA', na=False)]
    
    if 'CRM Order Type' in df.columns:
        df = df[df['CRM Order Type'].isin(['CREATE', 'MIGRATE'])]
    
    if 'Contact Number' in df.columns and 'Customer Name' in df.columns:
        c_map = df.loc[df['Contact Number'].notna() & (df['Contact Number'] != ''), ['Customer Name', 'Contact Number']].drop_duplicates('Customer Name')
        c_dict = dict(zip(c_map['Customer Name'], c_map['Contact Number']))
        
        def fill_contact(row):
            val = str(row['Contact Number'])
            if pd.isna(row['Contact Number']) or val.strip() == '' or val.lower() == 'nan':
                return c_dict.get(row['Customer Name'], row['Contact Number'])
            return row['Contact Number']
        
        df['Contact Number'] = df.apply(fill_contact, axis=1)
    
    return df, col_sc

def proses_modoroso(df):
    col_sc = 'SC Order No/Track ID/CSRM No'
    df = df[df[col_sc].astype(str).str.contains(r'-MO|-DO', na=False, case=False)].copy()
    
    if 'CRM Order Type' in df.columns:
        def detect_mo_do(val):
            s = str(val).upper()
            if '-MO' in s: return 'MO'
            if '-DO' in s: return 'DO'
            return 'MO'
        df['CRM Order Type'] = df[col_sc].apply(detect_mo_do)
    
    df['Mitra'] = 'TSEL'
    return df, 'Workorder'

def proses_wappr(df):
    col_sc = 'SC Order No/Track ID/CSRM No'
    df = df[df[col_sc].astype(str).str.contains('AO|PDA', na=False)]
    
    if 'Status' in df.columns:
        df = df[df['Status'].astype(str).str.strip().str.upper() == 'WAPPR']
    
    return df, 'Workorder'

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h2 style="margin: 0; font-size: 24px;">⚙️ Control Panel</h2>
            <p style="color: #64748b; font-size: 12px; margin-top: 5px;">WSA Fulfillment Pro</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    menu = st.radio(
        "Pilih Operasi:",
        ["WSA (Validation)", "MODOROSO", "WAPPR"],
        help="Pilih mode operasi sesuai kebutuhan"
    )
    
    st.markdown("---")
    
    curr_month = datetime.now().month
    prev_month = curr_month - 1 if curr_month > 1 else 12
    
    st.markdown("📅 **Filter Periode**")
    selected_months = st.multiselect(
        "Bulan:",
        options=list(range(1, 13)),
        default=[prev_month, curr_month],
        format_func=lambda x: ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"][x-1],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    with st.expander("ℹ️ Informasi"):
        st.markdown("""
            **Mode Operasi:**
            - **WSA**: Validasi data WSA
            - **MODOROSO**: Proses MO/DO
            - **WAPPR**: Filter WAPPR
            
            **Fitur:**
            - ✅ Auto cleansing
            - ✅ Validasi duplikat
            - ✅ Filter bulan
            - ✅ Export Excel
        """)

# ==========================================
# MAIN APP
# ==========================================
st.title(f"🚀 {menu}")
st.caption(f"Dashboard Processing | {datetime.now().strftime('%d %B %Y')}")

# Koneksi Google Sheets
client = get_gspread_client()
ws = None
connection_status = False

if client:
    try:
        sh = client.open("Salinan dari NEW GDOC WSA FULFILLMENT")
        if menu == "MODOROSO":
            target_sheet_name = "MODOROSO_JAKTIMSEL"
            try:
                ws = sh.worksheet(target_sheet_name)
            except:
                st.markdown(f'<div class="status-box error-box">❌ Sheet "{target_sheet_name}" tidak ditemukan!</div>', unsafe_allow_html=True)
                ws = None
        else:
            ws = sh.get_worksheet(0)
            target_sheet_name = ws.title if ws else "Unknown"

        if ws:
            st.markdown(f'<div class="status-box success-box">✅ TERHUBUNG | {target_sheet_name}</div>', unsafe_allow_html=True)
            connection_status = True
        else:
            connection_status = False

    except Exception as e:
        st.markdown(f'<div class="status-box error-box">❌ GAGAL AKSES: {e}</div>', unsafe_allow_html=True)
        connection_status = False
else:
    st.markdown(f'<div class="status-box error-box">❌ GAGAL TERHUBUNG - PERIKSA SECRETS</div>', unsafe_allow_html=True)
    connection_status = False

# Upload Section
st.markdown("---")
st.subheader("📤 Upload Data")

uploaded_file = st.file_uploader(
    f"Drop file {menu} di sini (XLSX/CSV)",
    type=["xlsx", "xls", "csv"],
    help="Upload file data Anda"
)

if connection_status and ws and uploaded_file:
    df_raw = pd.read_csv(uploaded_file) if uploaded_file.name.lower().endswith('.csv') else pd.read_excel(uploaded_file)
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Clean
        status_text.text("🧹 Membersihkan data...")
        progress_bar.progress(20)
        time.sleep(0.3)
        
        df = clean_common_data(df_raw.copy())
        
        # Step 2: Filter by mode
        status_text.text("🔍 Memfilter data...")
        progress_bar.progress(40)
        time.sleep(0.3)
        
        if menu == "WSA (Validation)":
            df_filtered, check_col = proses_wsa(df)
        elif menu == "MODOROSO":
            df_filtered, check_col = proses_modoroso(df)
        elif menu == "WAPPR":
            df_filtered, check_col = proses_wappr(df)
        
        # Step 3: Filter by month
        status_text.text("📅 Memfilter periode...")
        progress_bar.progress(60)
        time.sleep(0.3)
        
        if 'Date Created' in df_filtered.columns:
            df_filtered['Date Created DT'] = pd.to_datetime(df_filtered['Date Created'].astype(str).str.replace(r'\.0$', '', regex=True), errors='coerce')
            data_count_before = len(df_filtered)
            if selected_months:
                df_filtered = df_filtered[df_filtered['Date Created DT'].dt.month.isin(selected_months)]
            
            if data_count_before > 0 and len(df_filtered) == 0:
                st.warning(f"⚠️ {data_count_before} data ditemukan, tapi hilang karena filter bulan.")
            
            df_filtered['Date Created Display'] = df_filtered['Date Created DT'].dt.strftime('%d/%m/%Y %H:%M')
            df_filtered['Date Created'] = df_filtered['Date Created Display']
        
        # Step 4: Check duplicates
        status_text.text("🔗 Mengecek duplikat...")
        progress_bar.progress(80)
        time.sleep(0.3)
        
        google_data = ws.get_all_records()
        google_df = pd.DataFrame(google_data)
        
        if not google_df.empty and check_col in google_df.columns:
            existing_ids = google_df[check_col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().unique()
            
            col_sc = 'SC Order No/Track ID/CSRM No'
            if col_sc in df_filtered.columns:
                df_filtered[col_sc] = df_filtered[col_sc].astype(str).apply(lambda x: x.split('_')[0])
            
            df_final = df_filtered[~df_filtered[check_col].astype(str).str.strip().isin(existing_ids)].copy()
        else:
            col_sc = 'SC Order No/Track ID/CSRM No'
            if col_sc in df_filtered.columns:
                df_filtered[col_sc] = df_filtered[col_sc].astype(str).apply(lambda x: x.split('_')[0])
            df_final = df_filtered.copy()
        
        # Step 5: Finalize
        status_text.text("✅ Finalizing...")
        progress_bar.progress(100)
        time.sleep(0.3)
        
        status_text.empty()
        progress_bar.empty()
        
        # Reorder columns
        if menu == "MODOROSO":
            target_order = ['Date Created', 'Workorder', 'SC Order No/Track ID/CSRM No', 
                            'Service No.', 'CRM Order Type', 'Status', 'Address', 
                            'Customer Name', 'Workzone', 'Contact Number', 'Mitra']
        else:
            target_order = ['Date Created', 'Workorder', 'SC Order No/Track ID/CSRM No', 
                            'Service No.', 'CRM Order Type', 'Status', 'Address', 
                            'Customer Name', 'Workzone', 'Booking Date', 'Contact Number']
        
        cols_final = [c for c in target_order if c in df_final.columns]
        
        # METRICS
        st.markdown("---")
        st.subheader("📊 Ringkasan")
        
        m1, m2, m3 = st.columns(3)
        
        with m1:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-icon">📂</div>
                    <div class="metric-value">{len(df_filtered):,}</div>
                    <div class="metric-label">Data Filtered</div>
                </div>
            """, unsafe_allow_html=True)
        
        with m2:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-icon">✨</div>
                    <div class="metric-value success">{len(df_final):,}</div>
                    <div class="metric-label">Data Unik</div>
                </div>
            """, unsafe_allow_html=True)
        
        with m3:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-icon">🔗</div>
                    <div class="metric-value" style="font-size: 18px; margin-top: 10px;">{check_col}</div>
                    <div class="metric-label">Validasi By</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Preview
        st.markdown("---")
        st.subheader("📋 Preview Data")
        
        if 'Workzone' in df_final.columns:
            df_final = df_final.sort_values('Workzone')
        
        st.dataframe(df_final[cols_final], use_container_width=True, height=400)
        st.caption(f"Menampilkan {len(df_final):,} baris | {len(cols_final)} kolom")
        
        # Download
        st.markdown("---")
        st.subheader("💾 Download")
        
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df_final[cols_final].to_excel(writer, index=False, sheet_name='Data')
            worksheet = writer.sheets['Data']
            for i, col in enumerate(df_final[cols_final].columns):
                max_len = max(df_final[cols_final][col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, min(max_len, 50))
        
        col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
        with col_dl2:
            st.download_button(
                label=f"📥 Download {menu} (Excel)",
                data=excel_buffer.getvalue(),
                file_name=f"Cleaned_{menu.replace(' ', '_')}_{datetime.now().strftime('%d%m%Y_%H%M')}.xlsx",
                use_container_width=True
            )
        
        st.success(f"✅ Processing selesai! {len(df_final):,} data siap digunakan.")
        
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan: {e}")

elif not uploaded_file and connection_status:
    st.markdown("""
        <div class="info-box">
            <h4 style="margin-top: 0; color: #00d4ff;">👋 Selamat Datang!</h4>
            <p>Silakan upload file data Anda untuk memulai processing.</p>
            <p><strong>Format yang didukung:</strong> XLSX, XLS, CSV</p>
        </div>
    """, unsafe_allow_html=True)
