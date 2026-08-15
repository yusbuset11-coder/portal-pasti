import base64
from datetime import date
import json
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st

NAMA_SEKOLAH = "SMK Negeri 2 Bangkalan"
NAMA_GURU = "Yustinus Budi Setyanta"


def get_google_sheet_connection():
  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
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

  try:
    sh = get_google_sheet_connection()
    jurnal_ws = sh.worksheet("Jurnal_Mengajar")
    siswa_ws = sh.worksheet("Siswa")
    df_siswa = pd.DataFrame(siswa_ws.get_all_records())
    daftar_kelas = (
        df_siswa["Kelas"].dropna().unique().tolist()
        if "Kelas" in df_siswa.columns
        else ["Belum ada kelas"]
    )
  except Exception as e:
    st.error(f"Gagal memuat database: {e}")
    return

  tab1, tab2, tab3 = st.tabs(
      ["✍️ Input Jurnal", "📋 Daftar Jurnal", "📥 Export Laporan"]
  )

  # --- TAB 1: INPUT JURNAL ---
  with tab1:
    st.subheader("Form Input Jurnal Mengajar")

    with st.form("form_jurnal_mengajar", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        tanggal = st.date_input("Tanggal Mengajar", value=date.today())
        mata_pelajaran = st.text_input("Mata Pelajaran")
      with col2:
        kelas = st.selectbox("Kelas", options=daftar_kelas)
        jp_ke = st.text_input("JP Ke-")

      col_a, col_b = st.columns(2)
      with col_a:
        jumlah_hadir = st.number_input("Hadir", min_value=0, value=30, step=1)
      with col_b:
        jumlah_tidak_hadir = st.number_input(
            "Tidak Hadir", min_value=0, value=0, step=1
        )

      topik_materi = st.text_area("Topik / Materi Pokok")
      catatan_refleksi = st.text_area("Catatan / Refleksi")

      submitted = st.form_submit_button("💾 Simpan Jurnal")

      if submitted:
        try:
          row_data = [
              str(tanggal),
              NAMA_SEKOLAH,
              NAMA_GURU,
              mata_pelajaran,
              kelas,
              jp_ke,
              topik_materi,
              int(jumlah_hadir),
              int(jumlah_tidak_hadir),
              catatan_refleksi,
          ]
          jurnal_ws.append_row(row_data)
          st.success("✅ Jurnal tersimpan ke database!")
        except Exception as e:
          st.error(f"❌ Gagal: {e}")

  # --- TAB 2: DAFTAR & REKAPITULASI ---
  with tab2:
    try:
      data = jurnal_ws.get_all_records()
      if data:
        df = pd.DataFrame(data)
        df.columns = df.columns.str.strip()

        # Ubah nama kolom untuk tampilan
        df = df.rename(
            columns={
                "Jumlah_Hadir": "Hadir",
                "Jumlah_Tidak_Hadir": "Tidak_Hadir",
            }
        )

        kolom_tampil = [
            "Tanggal",
            "Mata_Pelajaran",
            "Kelas",
            "JP_Ke",
            "Topik_Materi",
            "Hadir",
            "Tidak_Hadir",
            "Catatan_Refleksi",
        ]
        kolom_tersedia = [col for col in kolom_tampil if col in df.columns]
        df_display = df[kolom_tersedia]

        search_query = st.text_input("🔍 Cari Mapel / Kelas")
        if search_query:
          df_display = df_display[
              df_display["Mata_Pelajaran"].str.contains(
                  search_query, case=False, na=False
              )
              | df_display["Kelas"].str.contains(
                  search_query, case=False, na=False
              )
          ]

        st.dataframe(df_display, use_container_width=True)
      else:
        st.info("Belum ada data jurnal tersimpan.")
    except Exception as e:
      st.error(f"Gagal memuat data: {e}")

  # --- TAB 3: EXPORT LAPORAN ---
  with tab3:
    try:
      data = jurnal_ws.get_all_records()
      if data:
        df_export = pd.DataFrame(data)
        df_export.columns = df_export.columns.str.strip()

        df_export = df_export.rename(
            columns={
                "Jumlah_Hadir": "Hadir",
                "Jumlah_Tidak_Hadir": "Tidak_Hadir",
            }
        )

        kolom_tampil = [
            "Tanggal",
            "Mata_Pelajaran",
            "Kelas",
            "JP_Ke",
            "Topik_Materi",
            "Hadir",
            "Tidak_Hadir",
            "Catatan_Refleksi",
        ]
        kolom_tersedia = [
            col for col in kolom_tampil if col in df_export.columns
        ]

        st.dataframe(df_export[kolom_tersedia], use_container_width=True)

        csv_data = df_export[kolom_tersedia].to_csv(index=False).encode("utf-8")
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