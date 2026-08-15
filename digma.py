import base64
from datetime import date
import io
import json
from google.oauth2.service_account import Credentials
import gspread
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import streamlit as st

# Default nama guru (tetap disimpan di database untuk rekam jejak)
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
                sekolah_pilihan,
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

        allowed_cols = [
            "Tanggal",
            "Sekolah",
            "Mata_Pelajaran",
            "Kelas",
            "JP_Ke",
            "Topik_Materi",
            "Hadir",
            "Tidak_Hadir",
            "Catatan",
        ]
        existing_cols = [col for col in allowed_cols if col in df.columns]
        df = df[existing_cols]

        if "Sekolah" in df.columns:
          list_sekolah_db = ["-- Semua Sekolah --"] + df[
              "Sekolah"
          ].dropna().unique().tolist()
          pilih_sekolah_filter = st.selectbox(
              "🔍 Filter Berdasarkan Sekolah", options=list_sekolah_db
          )
          if pilih_sekolah_filter != "-- Semua Sekolah --":
            df = df[df["Sekolah"] == pilih_sekolah_filter]

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

  # --- TAB 3: EXPORT LAPORAN SIAP CETAK & OTOMATIS RAPI ---
  with tab3:
    st.markdown("#### 📥 Cetak & Export Laporan ke Excel (.xlsx)")
    try:
      data = jurnal_ws.get_all_records()
      if data:
        df_export = pd.DataFrame(data)
        df_export.columns = df_export.columns.str.strip()

        allowed_cols = [
            "Tanggal",
            "Sekolah",
            "Mata_Pelajaran",
            "Kelas",
            "JP_Ke",
            "Topik_Materi",
            "Hadir",
            "Tidak_Hadir",
            "Catatan",
        ]
        existing_cols = [col for col in allowed_cols if col in df_export.columns]
        df_export = df_export[existing_cols]

        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
          if "Sekolah" in df_export.columns:
            list_sekolah_export = ["-- Semua Sekolah --"] + df_export[
                "Sekolah"
            ].dropna().unique().tolist()
            pilih_sekolah_ex = st.selectbox(
                "🏫 Filter Sekolah untuk Export",
                options=list_sekolah_export,
                key="ex_sekolah",
            )
            if pilih_sekolah_ex != "-- Semua Sekolah --":
              df_export = df_export[df_export["Sekolah"] == pilih_sekolah_ex]

        with col_ex2:
          opsi_filter_kelas_ex = ["-- Semua Kelas --"] + daftar_kelas
          pilih_kelas_ex = st.selectbox(
              "🏫 Filter Kelas untuk Export",
              options=opsi_filter_kelas_ex,
              key="ex_kelas",
          )
          if pilih_kelas_ex != "-- Semua Kelas --":
            df_export = df_export[df_export["Kelas"] == pilih_kelas_ex]

        st.dataframe(df_export, use_container_width=True, hide_index=True)

        # Proses styling profesional otomatis menggunakan openpyxl
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
          df_export.to_excel(writer, index=False, sheet_name="Jurnal Mengajar")

        # Ambil workbook yang baru dibuat untuk diformat
        output.seek(0)
        import openpyxl

        wb = openpyxl.load_workbook(output)
        ws = wb.active

        # Pengaturan Halaman Siap Cetak (Landscape & Fit to 1 Page Wide)
        ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0

        # Styling Header Tabel
        header_fill = PatternFill(
            start_color="1F4E78", end_color="1F4E78", fill_type="solid"
        )
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        thin_border = Border(
            left=Side(style="thin", color="D3D3D3"),
            right=Side(style="thin", color="D3D3D3"),
            top=Side(style="thin", color="D3D3D3"),
            bottom=Side(style="thin", color="D3D3D3"),
        )

        for col_num in range(1, ws.max_column + 1):
          cell = ws.cell(row=1, column=col_num)
          cell.fill = header_fill
          cell.font = header_font
          cell.alignment = Alignment(
              horizontal="center", vertical="center", wrap_text=True
          )
          cell.border = thin_border

        # Styling Data Isi Tabel & Auto-Fit Lebar Kolom
        for row in ws.iter_rows(
            min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column
        ):
          for cell in row:
            cell.font = Font(name="Calibri", size=11)
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center", wrap_text=True)

        # Auto-fit lebar kolom secara cerdas agar tidak terpotong
        for col in ws.columns:
          max_len = 0
          col_letter = get_column_letter(col[0].column)
          for cell in col:
            if cell.value:
              val_str = str(cell.value)
              max_len = max(max_len, len(val_str))
          # Berikan padding tambahan agar terlihat lega
          ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        # Simpan kembali ke BytesIO untuk tombol download Streamlit
        final_output = io.BytesIO()
        wb.save(final_output)
        excel_data = final_output.getvalue()

        nama_file_excel = f"Rekap_Jurnal_{pilih_sekolah_ex.replace(' ', '_')}_{pilih_kelas_ex.replace(' ', '_')}_{date.today()}.xlsx"

        st.download_button(
            label="📥 Download Laporan Excel Siap Cetak (.xlsx)",
            data=excel_data,
            file_name=nama_file_excel,
            mime=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
      else:
        st.info("Tidak ada data untuk diexport.")
    except Exception as e:
      st.error(f"Gagal menyiapkan data untuk export: {e}")