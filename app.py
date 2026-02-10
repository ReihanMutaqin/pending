import webbrowser
import urllib.parse

def generate_email_intent():
    # --- INPUT DATA ---
    witel = input("1. WITEL: ") or "JAKARTA SELATAN"
    sto = input("2. STO: ") or "JAG"
    order_id = input("3. Order ID: ")
    
    print("\nPilih Status OSM:")
    print("1. WorkForceTask, 2. CreateTTTaskForTom, 3. Gettom, 4. GetSOMTTRESPONE, 5. COMPLATED")
    osm_idx = input("Nomor Status: ")
    osm_list = ["WorkForceTask", "CreateTTTaskForTom", "Gettom", "GetSOMTTRESPONE", "COMPLATED"]
    status_osm = osm_list[int(osm_idx)-1] if osm_idx else "WorkForceTask"

    wonum = input("5. WONUM: ")
    
    print("\nPilih Status BIMA:")
    bima_list = ["WAPPR", "STARTWORK", "WORKFAIL", "PENDWORK", "CAONTWORK", "CANCLWORK", "INSTCOMP", "ACTCOMP", "VALSTART", "VALCOMP", "DEINSTCOMP", "COMPWORK"]
    for i, s in enumerate(bima_list): print(f"{i+1}. {s}")
    bima_idx = input("Nomor Status: ")
    status_bima = bima_list[int(bima_idx)-1] if bima_idx else "WAPPR"

    # --- GRUP DINAMIS (7, 8, 9) ---
    layanan_data = ""
    while True:
        nd = input("\n7. ND: ")
        rfs = input("8. BI ID RFS: ")
        cfs = input("9. BI ID CFS: ")
        layanan_data += f"7. ND  {nd}\r\n8. BI ID RFS     {rfs}\r\n9. BI ID CFS      {cfs}\r\n"
        
        tambah = input("Tambah Grup ND lagi? (y/n): ")
        if tambah.lower() != 'y': break

    tiket_bima = input("10. TIKET BIMA: ")
    ibooster = input("11. CEK IBOOSTER (Online/Offline/dll): ")
    layanan = input("12. LAYANAN DO: ")
    nama_hd = "HD ISH REIHAN MUTAQIN"

    # --- PENERIMA ---
    tujuan = "novi@tif.co.id,yosia.bagariang@tif.co.id,rocdua2@gmail.com"
    subject = f"OPEN BI - {nd}"

    # --- MERAKIT BODY EMAIL ---
    body = f"""1. WITEL {witel}
2. STO {sto}
3. Order ID  {order_id}
4. STATUS ORDER ID (OSM)     >  ( {status_osm} )

5. WONUM  {wonum}
6. STATUS WONUM (BIMA)      > ( {status_bima} )

{layanan_data}
10. TIKET BIMA   {tiket_bima}
11. CEK IBOOSTER   > ({ibooster})
12. LAYANAN DO > ({layanan})

13. [PASTE GAMBAR DI SINI]

DARI      : {nama_hd}
"""

    # --- MEMBUKA APLIKASI EMAIL ---
    # Mengubah teks menjadi format URL
    subject_encoded = urllib.parse.quote(subject)
    body_encoded = urllib.parse.quote(body)
    
    mail_to_url = f"mailto:{tujuan}?subject={subject_encoded}&body={body_encoded}"
    
    print("\nSedang membuka draf email...")
    webbrowser.open(mail_to_url)

if __name__ == "__main__":
    generate_email_intent()
