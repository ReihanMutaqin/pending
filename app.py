import streamlit as st
import urllib.parse

# Konfigurasi Halaman
st.set_page_config(page_title="Tool OPEN BI - Reihan", page_icon="📧")

st.title("📧 Generator Draf Email OPEN BI")
st.info("Isi data, lalu klik tombol di bawah untuk membuka draf email.")

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

# --- 2. GRUP DINAMIS (Penomoran Berlanjut & Tukar RFS/CFS) ---
st.subheader("Data Layanan (ND, BI CFS, BI RFS)")

if 'groups' not in st.session_state:
    st.session_state.groups = 1

def add_group():
    st.session_state.groups += 1

def remove_group():
    if st.session_state.groups > 1:
        st.session_state.groups -= 1

group_list = []
current_num = 7  # Mulai penomoran dari nomor 7

for i in range(st.session_state.groups):
    with st.expander(f"Grup Data {i+1} (No. {current_num}-{current_num+2})", expanded=True):
        g_nd = st.text_input(f"{current_num}. ND", key=f"nd_{i}")
        g_cfs = st.text_input(f"{current_num+1}. BI ID CFS", key=f"cfs_{i}") # CFS Sekarang di atas RFS
        g_rfs = st.text_input(f"{current_num+2}. BI ID RFS", key=f"rfs_{i}")
        
        group_list.append({
            "num_nd": current_num, "nd": g_nd, 
            "num_cfs": current_num+1, "cfs": g_cfs, 
            "num_rfs": current_num+2, "rfs": g_rfs
        })
        current_num += 3 # Penomoran berlanjut ke angka berikutnya

c1, c2 = st.columns(2)
with c1:
    st.button("➕ Tambah Grup", on_click=add_group, use_container_width=True)
with c2:
    st.button("🗑️ Hapus Grup Terakhir", on_click=remove_group, use_container_width=True)

# --- 3. DATA TAMBAHAN (Nomor mengikuti urutan terakhir) ---
st.divider()
last_num = current_num
tiket_bima = st.text_input(f"{last_num}. TIKET BIMA", value="INF007196948")
ibooster = st.selectbox(f"{last_num+1}. CEK IBOOSTER", 
                         ["Online", "los", "Dying Gasp", "Offline", "Tidak ada datek", "Datek voice belum ims", "Unknow"])

st.write(f"{last_num+2}. LAYANAN DO")
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

body_pesan = f"1. WITEL {witel}\r\n"
body_pesan += f"2. STO {sto}\r\n"
body_pesan += f"3. Order ID  {order_id}\r\n"
body_pesan += f"4. STATUS ORDER ID (OSM)     >  ( {status_osm} )\r\n\r\n"
body_pesan += f"5. WONUM  {wonum}\r\n"
body_pesan += f"6. STATUS WONUM (BIMA)      > ( {status_bima} )\r\n\r\n"

for g in group_list:
    body_pesan += f"{g['num_nd']}. ND  {g['nd']}\r\n"
    body_pesan += f"{g['num_cfs']}. BI ID CFS      {g['cfs']}\r\n"
    body_pesan += f"{g['num_rfs']}. BI ID RFS     {g['rfs']}\r\n"

body_pesan += f"\r\n{last_num}. TIKET BIMA   {tiket_bima}\r\n"
body_pesan += f"{last_num+1}. CEK IBOOSTER   > ({ibooster})\r\n"
body_pesan += f"{last_num+2}. LAYANAN DO > ({layanan_final})\r\n\r\n"
body_pesan += f"{last_num+3}. [PASTE GAMBAR SS DI SINI]\r\n\r\n"
body_pesan += f"DARI      : {nama_hd}"

# URL Encoding
first_nd = group_list[0]['nd'] if group_list[0]['nd'] else sto
subject = f"OPEN BI - {first_nd}"
mailto_link = f"mailto:{tujuan}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body_pesan)}"

st.divider()
st.subheader("Preview Draft:")
st.code(body_pesan)

st.link_button("🚀 BUKA GMAIL / OUTLOOK", mailto_link, use_container_width=True)
