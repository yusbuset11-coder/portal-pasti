import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

def get_google_sheet_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credentials_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Database_PASTI_Pusat")
    return sheet

def render_digma_module():
    st.markdown("### 📊 DIGMA: Digitalisasi Jurnal Mengajar")
    
    tab1, tab2, tab3 = st.tabs([
        "✍️ Input Jurnal Mengajar", 
        "📋 Daftar & Rekapitulasi Jurnal", 
        "📥 Cetak & Export Laporan"
    ])
    
    try:
        sh = get_google_sheet_connection()
        worksheet = sh.worksheet("Jurnal_Mengajar")
    except Exception as e:
        st.error(f"Gagal terhubung ke Google Sheets: {e}")
        return

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
                kelas = st.text_input("Kelas", placeholder="Contoh: X PPLG 1")
            with col2:
                jumlah_hadir = st.number_input("Jumlah Siswa Hadir", min_value=0, value=30, step=1)
            with col3:
                jumlah_tidak_hadir = st.number_input("Jumlah Siswa Tidak Hadir", min_value=0, value=0, step=1)
            
            topik_materi = st.text_area("Topik / Materi Pokok", placeholder="Tuliskan topik atau tujuan pembelajaran...")
            catatan_refleksi = st.text_area("Catatan Kejadian / Refleksi Pembelajaran", placeholder="Catatan penting atau refleksi kelas...")
            
            submitted = st.form_submit_button("💾 Simpan Jurnal Mengajar")
            
            if submitted:
                if not mata_pelajaran or not kelas or not topik_materi:
                    st.warning("Mohon lengkapi Mata Pelajaran, Kelas, dan Topik/Materi terlebih dahulu!")
                else:
                    try:
                        row_data = [
                            str(tanggal),
                            nama_sekolah,
                            nama_guru,
                            mata_pelajaran,
                            kelas,
                            topik_materi,
                            int(jumlah_hadir),
                            int(jumlah_tidak_hadir),
                            catatan_refleksi
                        ]
                        worksheet.append_row(row_data)
                        st.success("✅ Jurnal mengajar berhasil disimpan ke Database Pusat!")
                    except Exception as e:
                        st.error(f"❌ Gagal menyimpan jurnal ke Database: {e}")

    # --- TAB 2: DAFTAR & REKAPITULASI ---
    with tab2:
        st.subheader("Daftar & Rekapitulasi Jurnal Mengajar")
        try:
            data = worksheet.get_all_records()
            if data:
                df = pd.DataFrame(data)
                search_query = st.text_input("🔍 Cari berdasarkan Nama Guru / Mapel", value="")
                if search_query:
                    df = df[
                        df["Nama_Guru"].str.contains(search_query, case=False, na=False) | 
                        df["Mata_Pelajaran"].str.contains(search_query, case=False, na=False)
                    ]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Belum ada data Jurnal Mengajar yang tersimpan di database.")
        except Exception as e:
            st.error(f"Gagal memuat data dari Google Sheets: {e}")

    # --- TAB 3: EXPORT LAPORAN ---
    with tab3:
        st.subheader("Cetak & Export Laporan Pembelajaran")
        try:
            data = worksheet.get_all_records()
            if data:
                df_export = pd.DataFrame(data)
                st.dataframe(df_export, use_container_width=True)
                csv_data = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Rekap Jurnal (.csv)",
                    data=csv_data,
                    file_name=f"Rekap_Jurnal_Mengajar_{date.today()}.csv",
                    mime="text/csv",
                )
            else:
                st.info("Tidak ada data untuk diexport.")
        except Exception as e:
            st.error(f"Gagal menyiapkan data untuk export: {e}")