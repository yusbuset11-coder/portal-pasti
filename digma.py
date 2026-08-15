import streamlit as st
import base64
import json
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

def get_google_sheet_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    # Mengambil kredensial dari secrets
    credentials_dict = json.loads(
        base64.b64decode(st.secrets["gcp_base64"]).decode("utf-8")
    )
    creds = Credentials.from_service_account_info(
        credentials_dict, scopes=scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("Database_PASTI_Pusat")
    return sheet

def render_digma_module():
    st.markdown("### 📊 DIGMA: Digitalisasi Jurnal Mengajar")
    
    # Koneksi ke Sheets
    try:
        sh = get_google_sheet_connection()
        jurnal_ws = sh.worksheet("Jurnal_Mengajar")
        siswa_ws = sh.worksheet("Siswa")
        
        # Mengambil daftar kelas dari sheet Siswa
        df_siswa = pd.DataFrame(siswa_ws.get_all_records())
        if "Kelas" in df_siswa.columns:
            daftar_kelas = df_siswa["Kelas"].dropna().unique().tolist()
        else:
            daftar_kelas = ["Belum ada data kelas"]
            
    except Exception as e:
        st.error(f"Gagal memuat data dari database: {e}")
        return

    tab1, tab2, tab3 = st.tabs([
        "✍️ Input Jurnal Mengajar", 
        "📋 Daftar & Rekapitulasi Jurnal", 
        "📥 Cetak & Export Laporan"
    ])
    
    # --- TAB 1: INPUT JURNAL ---
    with tab1:
        st.subheader("Form Input Jurnal Mengajar Harian")
        
        col_id1, col_id2 = st.columns(2)
        with col_id1:
            nama_sekolah = st.text_input("Nama Sekolah", value="SMK Negeri 2 Bangkalan")
            nama_guru = st.text_input("Nama Guru", value="Yustinus Budi Setyanta")
        with col_id2:
            mata_pelajaran = st.text_input("Mata Pelajaran", placeholder="Contoh: Pendidikan Pancasila")
            tanggal = st.date_input("Tanggal Mengajar", value=date.today())
            
        st.markdown("---")
        
        with st.form("form_jurnal_mengajar", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                # Menggunakan selectbox dengan data dari sheet Siswa
                kelas = st.selectbox("Kelas", options=daftar_kelas)
            with col2:
                jp_ke = st.text_input("JP Ke-", placeholder="Contoh: 1-2")
                jumlah_hadir = st.number_input("Hadir", min_value=0, value=30, step=1)
            with col3:
                jumlah_tidak_hadir = st.number_input("Tidak Hadir", min_value=0, value=0, step=1)
            
            topik_materi = st.text_area("Topik / Materi Pokok", placeholder="Tuliskan topik pembelajaran...")
            catatan_refleksi = st.text_area("Catatan / Refleksi", placeholder="Catatan penting...")
            
            submitted = st.form_submit_button("💾 Simpan Jurnal Mengajar")
            
            if submitted:
                if not mata_pelajaran or not topik_materi:
                    st.warning("Mohon lengkapi Mata Pelajaran dan Topik Materi!")
                else:
                    try:
                        # Urutan sesuai Header Baru: 
                        # Tanggal - Sekolah - Nama_Guru - Mata_Pelajaran - Kelas - JP_Ke - Topik_Materi - Hadir - Tidak_Hadir - Catatan
                        row_data = [
                            str(tanggal),
                            nama_sekolah,
                            nama_guru,
                            mata_pelajaran,
                            kelas,
                            jp_ke,
                            topik_materi,
                            int(jumlah_hadir),
                            int(jumlah_tidak_hadir),
                            catatan_refleksi
                        ]
                        jurnal_ws.append_row(row_data)
                        st.success("✅ Jurnal berhasil disimpan!")
                    except Exception as e:
                        st.error(f"❌ Gagal menyimpan: {e}")

    # --- TAB 2: DAFTAR & REKAPITULASI ---
    with tab2:
        st.subheader("Daftar & Rekapitulasi Jurnal")
        try:
            data = jurnal_ws.get_all_records()
            if data:
                df = pd.DataFrame(data)
                search_query = st.text_input("🔍 Cari berdasarkan Mapel / Kelas", value="")
                if search_query:
                    df = df[
                        df["Mata_Pelajaran"].str.contains(search_query, case=False, na=False) | 
                        df["Kelas"].str.contains(search_query, case=False, na=False)
                    ]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Belum ada data.")
        except Exception as e:
            st.error(f"Gagal memuat data: {e}")

    # --- TAB 3: EXPORT LAPORAN ---
    with tab3:
        st.subheader("Cetak & Export Laporan")
        try:
            data = jurnal_ws.get_all_records()
            if data:
                df_export = pd.DataFrame(data)
                st.dataframe(df_export, use_container_width=True)
                csv_data = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Rekap (.csv)",
                    data=csv_data,
                    file_name=f"Rekap_Jurnal_{date.today()}.csv",
                    mime="text/csv",
                )
            else:
                st.info("Tidak ada data untuk diexport.")
        except Exception as e:
            st.error(f"Gagal export: {e}")