import streamlit as st
import urllib.parse

# Konfigurasi Halaman
st.set_page_config(page_title="Tool OPEN BI - Reihan", page_icon="📧")

st.title("📧 Generator Draf Email OPEN BI")
st.info("Isi data di bawah, lalu klik tombol untuk otomatis membuka draf di Gmail/Outlook.")

# --- 1. DATA UTAMA ---
col1, col2 = st.columns(2)
with col1:
    witel = st.text_input("1. WITEL", value="JAKARTA SELATAN")
    sto = st.text_input("2. STO", value="JAG")
with col2:
    order_id = st.text_input("3. Order ID", value="A301260205100629935229750-MOi1260205100630602d5dcf0_65638107")
    status_osm = st.selectbox("4. STATUS ORDER ID (OSM)", 
                                ["WorkForceTask", "CreateTTTaskForTom", "Gettom", "GetSOMTTRESPONE", "COMPLATED"])

col3, col4 = st.columns(2)
with col3:
    wonum = st.text_input("5. WONUM", value="WO045406357")
with col4:
    status_bima = st.selectbox("6. STATUS WONUM (BIMA)", 
                                 ["WAPPR", "STARTWORK", "WORKFAIL", "PENDWORK", "CAONTWORK", "CANCLWORK", "INSTCOMP", "ACTCOMP", "VALSTART", "VALCOMP", "DEINSTCOMP", "COMPWORK"])

# --- 2. GRUP DINAMIS (7, 8, 9) ---
st.subheader("Data Layanan (ND, BI RFS, BI CFS)")
if 'groups' not in st.session_state:
    st.session_state.groups = 1

def add_group():
    st.session_state.groups += 1

group_list = []
for i in range(st.session_state.groups):
    with st.expander(f"Grup Data {i+1}", expanded=True):
        g_nd = st.text_input(f"7. ND (Grup {i+1})", key=f"nd_{i}")
        g_rfs = st.text_input(f"8. BI ID RFS (Grup {i+1})", key=f"rfs_{i}")
        g_cfs = st.text_input(f"9. BI ID CFS (Grup {i+1})", key=f"cfs_{i}")
        group_list.append({"nd": g_nd, "rfs": g_rfs, "cfs": g_cfs})

st.button("➕ Tambah Grup Data (7, 8, 9)", on_click=add_group)

# --- 3. DATA TAMBAHAN ---
st.divider()
tiket_bima = st.text_input("10. TIKET BIMA", value="INF007196948")
ibooster = st.selectbox("11. CEK IBOOSTER", 
                         ["Online", "los", "Dying Gasp", "Offline", "Tidak ada datek", "Datek voice belum ims", "Unknow"])

st.write("12. LAYANAN DO")
layanan_opts = ["VOICE", "INTERNET", "IPTV", "OTT"]
sel_layanan = []
l_cols = st.columns(4)
for idx, opt in enumerate(layanan_opts):
    if l_cols[idx].checkbox(opt):
        sel_layanan.append(opt)
layanan_final = " + ".join(sel_layanan) if sel_layanan else "VOICE"

nama_hd = st.text_input("DARI (Nama HD)", value="HD ISH REIHAN MUTAQIN")

# --- 4. GENERATOR LOGIC ---
tujuan = "novi@tif.co.id,yosia.bagariang@tif.co.id,rocdua2@gmail.com"

# Merakit Body Pesan
body_pesan = f"1. WITEL {witel}\r\n"
body_pesan += f"2. STO {sto}\r\n"
body_pesan += f"3. Order ID  {order_id}\r\n"
body_pesan += f"4. STATUS ORDER ID (OSM)     >  ( {status_osm} )\r\n\r\n"
body_pesan += f"5. WONUM  {wonum}\r\n"
body_pesan += f"6. STATUS WONUM (BIMA)      > ( {status_bima} )\r\n\r\n"

for idx, g in enumerate(group_list):
    body_pesan += f"7. ND  {g['nd']}\r\n"
    body_pesan += f"8. BI ID RFS     {g['rfs']}\r\n"
    body_pesan += f"9. BI ID CFS      {g['cfs']}\r\n"

body_pesan += f"\r\n10. TIKET BIMA   {tiket_bima}\r\n"
body_pesan += f"11. CEK IBOOSTER   > ({ibooster})\r\n"
body_pesan += f"12. LAYANAN DO > ({layanan_final})\r\n\r\n"
body_pesan += f"13. [PASTE GAMBAR SS DI SINI]\r\n\r\n"
body_pesan += f"DARI      : {nama_hd}"

# URL Encoding untuk Mailto
subject = f"OPEN BI - {group_list[0]['nd'] if group_list[0]['nd'] else sto}"
mailto_link = f"mailto:{tujuan}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body_pesan)}"

st.divider()
st.subheader("Preview Draft:")
st.code(body_pesan)

# Tombol Eksekusi
st.link_button("🚀 BUKA GMAIL / OUTLOOK", mailto_link, use_container_width=True)

st.caption("Setelah klik tombol di atas, aplikasi email akan terbuka. Jangan lupa tekan Ctrl+V untuk paste gambar di poin 13.")
