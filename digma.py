import base64
from datetime import date
import json
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st

# Default nama guru
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
    st.markdown("#### 📝 Form Input Jurnal Mengajar Harian")

    with st.form("form_jurnal_mengajar", clear_on_submit=True):
      st.markdown("##### 🏫 Lokasi & Jadwal Mengajar")
      col_s1, col_s2 = st.columns(2)
      with col_s1:
        # Diubah menjadi text_input agar bisa bebas mengetik nama sekolah apa saja
        sekolah_pilihan = st.text_input(
            "Nama Sekolah Tempat Mengajar",
            value="SMK Negeri 2 Bangkalan",
            placeholder="Contoh: SMK Negeri 1 Kwanyar",
        )
      with col_s2:
        tanggal = st.date_input("📅 Tanggal Mengajar", value=date.today())

      col1, col2, col3 = st.columns(3)
      with col1:
        kelas = st.selectbox("🏫 Kelas", options=daftar_kelas)
      with col2:
        jp_ke = st.text_input(
            "⏱️ Jam Pelajaran (JP Ke-)", placeholder="Contoh: 1-2"
        )
      with col3:
        mata_pelajaran = st.text_input(
            "📖 Mata Pelajaran", placeholder="Contoh: Pendidikan Pancasila"
        )

      st.markdown("##### 👥 Kehadiran Siswa")
      col_a, col_b = st.columns(2)
      with col_a:
        hadir = st.number_input(
            "✅ Siswa Hadir", min_value=0, value=30, step=1
        )
      with col_b:
        tidak_hadir = st.number_input(
            "❌ Siswa Tidak Hadir", min_value=0, value=0, step=1
        )

      st.markdown("##### 📝 Materi & Refleksi Pembelajaran")
      topik_materi = st.text_area(
          "💡 Topik / Materi Pokok",
          placeholder="Tuliskan topik atau tujuan pembelajaran hari ini...",
      )
      catatan = st.text_area(
          "📌 Catatan / Refleksi",
          placeholder="Catatan tambahan atau refleksi kegiatan kelas...",
      )

      st.markdown("")
      submitted = st.form_submit_button(
          "💾 Simpan Jurnal Mengajar", use_container_width=True
      )

      if submitted:
        if not sekolah_pilihan or not mata_pelajaran or not topik_materi:
          st.warning(
              "⚠️ Mohon lengkapi Nama Sekolah, Mata Pelajaran, dan"
              " Topik/Materi!"
          )
        else:
          try:
            row_data = [
                str(tanggal),
                sekolah_pilihan,  # Menyimpan teks sekolah yang diinput bebas
                NAMA_GURU,
                mata_pelajaran,
                kelas,
                jp_ke,
                topik_materi,
                int(hadir),
                int(tidak_hadir),
                catatan,
            ]
            jurnal_ws.append_row(row_data)
            st.success("✅ Jurnal mengajar berhasil disimpan ke Database Pusat!")
            st.balloons()
          except Exception as e:
            st.error(f"❌ Gagal menyimpan jurnal ke Database: {e}")

  # --- TAB 2: DAFTAR & REKAPITULASI ---
  with tab2:
    st.markdown("#### 📋 Daftar & Rekapitulasi Jurnal Mengajar")
    try:
      data = jurnal_ws.get_all_records()
      if data:
        df = pd.DataFrame(data)
        df.columns = df.columns.str.strip()

        # Filter Berdasarkan Sekolah
        if "Sekolah" in df.columns:
          list_sekolah_db = ["-- Semua Sekolah --"] + df[
              "Sekolah"
          ].dropna().unique().tolist()
          pilih_sekolah_filter = st.selectbox(
              "🔍 Filter Berdasarkan Sekolah", options=list_sekolah_db
          )
          if pilih_sekolah_filter != "-- Semua Sekolah --":
            df = df[df["Sekolah"] == pilih_sekolah_filter]

        # Filter Berdasarkan Kelas
        opsi_filter_kelas = ["-- Semua Kelas --"] + daftar_kelas
        pilih_kelas = st.selectbox(
            "🔍 Filter Berdasarkan Kelas", options=opsi_filter_kelas
        )
        if pilih_kelas != "-- Semua Kelas --":
          df = df[df["Kelas"] == pilih_kelas]

        st.dataframe(df, use_container_width=True, hide_index=True)
      else:
        st.info("Belum ada data Jurnal Mengajar yang tersimpan di database.")
    except Exception as e:
      st.error(f"Gagal memuat data dari Google Sheets: {e}")

  # --- TAB 3: EXPORT LAPORAN ---
  with tab3:
    st.markdown("#### 📥 Cetak & Export Laporan Pembelajaran")
    try:
      data = jurnal_ws.get_all_records()
      if data:
        df_export = pd.DataFrame(data)
        df_export.columns = df_export.columns.str.strip()

        st.dataframe(df_export, use_container_width=True, hide_index=True)

        csv_data = df_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Seluruh Rekap Jurnal (.csv)",
            data=csv_data,
            file_name=f"Rekap_Jurnal_Mengajar_{date.today()}.csv",
            mime="text/csv",
        )
      else:
        st.info("Tidak ada data untuk diexport.")
    except Exception as e:
      st.error(f"Gagal menyiapkan data untuk export: {e}")