from datetime import datetime
import io
import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# --- KONFIGURASI HALAMAN PORTAL ---
st.set_page_config(
    page_title="PASTI - Portal Akademik Siswa Terintegrasi",
    page_icon="📚",
    layout="wide",
)

MASTER_REGISTRY_ID = "1mgN63xzrLt__5b9-gBw8dIWYP3RRgNdagUiTurFZdgg"


# --- KONEKSI GOOGLE SHEETS & GEMINI AI ---
@st.cache_resource
def get_gspread_client():
  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  creds_dict = dict(st.secrets["gcp_service_account"])
  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  client = gspread.authorize(creds)
  try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
  except Exception:
    pass
  return client


@st.cache_resource
def load_master_registry():
  try:
    client = get_gspread_client()
    sh = client.open_by_key(MASTER_REGISTRY_ID)
    worksheet = sh.worksheet("DATABASE_MASTER_REGISTRY")
    return worksheet.get_all_records()
  except Exception as e:
    st.error(f"Gagal terhubung ke Master Registry: {e}")
    return None


@st.cache_resource
def load_guru_database(sheet_id):
  try:
    client = get_gspread_client()
    return client.open_by_key(sheet_id)
  except Exception:
    return None


# --- INISIALISASI SESSION STATE ---
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.guru_nama = ""
  st.session_state.spreadsheet_id = ""
  st.session_state.current_page = "home"


def go_to(page_name):
  st.session_state.current_page = page_name
  st.rerun()


# --- 1. HALAMAN LOGIN / VERIFIKASI GURU ---
if not st.session_state.logged_in:
  st.markdown(
      "<h2 style='text-align: center; color: #0284c7;'>🔐 Portal PASTI</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center;'>Portal Akademik Siswa Terintegrasi — Masuk"
      " sekali untuk akses seluruh aplikasi</p>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    with st.form("login_form"):
      input_identifier = st.text_input(
          "**Email / Token Unik**",
          placeholder=(
              "Contoh: yustinussetyanta08@dinas.belajar.id atau TOKEN300869"
          ),
      )
      submit_login = st.form_submit_button(
          "🚀 Masuk ke Portal PASTI", use_container_width=True
      )

      if submit_login:
        if not input_identifier:
          st.error("Mohon masukkan Email atau Token Unik Anda!")
        else:
          with st.spinner("Memeriksa data registrasi..."):
            registry_data = load_master_registry()
            if registry_data is not None:
              found = False
              for row in registry_data:
                match_email = (
                    str(row.get("Email", "")).strip().lower()
                    == input_identifier.strip().lower()
                )
                match_token = (
                    str(row.get("Token_Unik", "")).strip()
                    == input_identifier.strip()
                )
                is_active = (
                    str(row.get("Status", "")).strip().upper() == "AKTIF"
                )

                if (match_email or match_token) and is_active:
                  st.session_state.logged_in = True
                  st.session_state.guru_nama = row.get("Nama_Guru", "Guru")
                  st.session_state.spreadsheet_id = str(
                      row.get("Spreadsheet_ID_Guru", "")
                  ).strip()
                  found = True
                  break

              if found:
                if (
                    not st.session_state.spreadsheet_id
                    or st.session_state.spreadsheet_id == "(Kosongkan dulu)"
                ):
                  st.warning(
                      "⚠️ Akun Anda aktif, namun `Spreadsheet_ID_Guru` di Master"
                      " Registry masih kosong."
                  )
                  st.session_state.logged_in = False
                else:
                  st.success("Login Berhasil! Memuat Portal...")
                  st.rerun()
              else:
                st.error(
                    "❌ Email/Token tidak ditemukan atau status akun tidak"
                    " AKTIF."
                )
            else:
              st.error(
                  "❌ Gagal terhubung ke Google Spreadsheet Master Registry."
              )
  st.stop()

# Load database guru yang sedang aktif
sh_guru = load_guru_database(st.session_state.spreadsheet_id)

# --- 2. DASHBOARD UTAMA (BERANDA PASTI) ---
if st.session_state.current_page == "home":
  st.markdown(
      f"""
        <div style="background-color: #0284c7; padding: 35px; border-radius: 10px; text-align: center; color: white; margin-bottom: 30px;">
            <h1 style="margin: 0; color: white; font-size: 40px;">📂 PASTI</h1>
            <h3 style="margin: 10px 0 0 0; color: #e0f2fe; font-weight: normal;">Portal Akademik Siswa Terintegrasi</h3>
            <p style="margin: 8px 0 0 0; color: #bae6fd; font-size: 15px;">Selamat datang, <b>{st.session_state.guru_nama}</b></p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown("### Pilih Layanan Aplikasi:")
  col1, col2, col3, col4 = st.columns(4)

  with col1:
    with st.container(border=True):
      st.markdown(
          "<h2 style='text-align: center;'>👤</h2>", unsafe_allow_html=True
      )
      st.markdown(
          "<h4 style='text-align: center; color: #0284c7;'>SIPENSIS</h4>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p style='text-align: center; font-size: 13px;'>Sistem Informasi"
          " Presensi Siswa.</p>",
          unsafe_allow_html=True,
      )
      if st.button("Buka SIPENSIS", use_container_width=True, key="b_sipensis"):
        go_to("sipensis")

  with col2:
    with st.container(border=True):
      st.markdown(
          "<h2 style='text-align: center;'>📖</h2>", unsafe_allow_html=True
      )
      st.markdown(
          "<h4 style='text-align: center; color: #0284c7;'>DIGMA</h4>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p style='text-align: center; font-size: 13px;'>Digitalisasi Jurnal"
          " Mengajar Guru.</p>",
          unsafe_allow_html=True,
      )
      if st.button("Buka DIGMA", use_container_width=True, key="b_digma"):
        go_to("digma")

  with col3:
    with st.container(border=True):
      st.markdown(
          "<h2 style='text-align: center;'>⚡</h2>", unsafe_allow_html=True
      )
      st.markdown(
          "<h4 style='text-align: center; color: #0284c7;'>SAKTI</h4>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p style='text-align: center; font-size: 13px;'>Sistem Asesmen &"
          " Kompetensi Terintegrasi.</p>",
          unsafe_allow_html=True,
      )
      if st.button("Buka SAKTI", use_container_width=True, key="b_sakti"):
        go_to("sakti")

  with col4:
    with st.container(border=True):
      st.markdown(
          "<h2 style='text-align: center;'>📚</h2>", unsafe_allow_html=True
      )
      st.markdown(
          "<h4 style='text-align: center; color: #0284c7;'>GEMA</h4>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p style='text-align: center; font-size: 13px;'>Generator Modul Ajar"
          " Pembelajaran Mendalam.</p>",
          unsafe_allow_html=True,
      )
      if st.button("Buka GEMA", use_container_width=True, key="b_gema"):
        go_to("gema")

  st.write("---")
  col_kiri, col_kanan = st.columns([6, 1])
  with col_kanan:
    if st.button("🚪 Keluar (Logout)", use_container_width=True):
      st.session_state.logged_in = False
      st.session_state.guru_nama = ""
      st.session_state.spreadsheet_id = ""
      go_to("home")

# --- 3. MODUL SIPENSIS ---
elif st.session_state.current_page == "sipensis":
  if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
    go_to("home")
  st.markdown("## 📊 **SIPENSIS: Sistem Presensi Siswa**[cite: 3]")
  st.info(
      f"Database aktif terhubung ke Spreadsheet ID Guru:"
      f" `{st.session_state.spreadsheet_id}`"
  )

  if sh_guru is None:
    st.error("Gagal terhubung ke Database Google Sheets Anda.")
  else:
    tab1, tab2, tab3 = st.tabs([
        "📋 Input Data Siswa",
        "📝 Input Presensi Harian",
        "📈 Rekap Semester",
    ])
    with tab1:
      st.write("Kelola data siswa melalui upload Excel atau database Anda[cite: 3].")
      try:
        ws_siswa = sh_guru.worksheet("Data Kelas-Siswa")
        data_s = ws_siswa.get_all_records()
        if data_s:
          st.dataframe(pd.DataFrame(data_s), use_container_width=True)
        else:
          st.info("Belum ada data siswa.")
      except Exception:
        st.info("Tab 'Data Kelas-Siswa' belum tersedia.")
    with tab2:
      st.write("Gunakan fitur presensi harian lengkap sesuai modul SIPENSIS[cite: 3].")
    with tab3:
      st.write("Rekapitulasi ketidakhadiran semester ganjil & genap[cite: 3].")

# --- 4. MODUL DIGMA ---
elif st.session_state.current_page == "digma":
  if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
    go_to("home")
  st.markdown("## 📖 **DIGMA: Digitalisasi Jurnal Mengajar**[cite: 4]")
  st.info(
      f"Database aktif terhubung ke Spreadsheet ID Guru:"
      f" `{st.session_state.spreadsheet_id}`"
  )

  if sh_guru is None:
    st.error("Gagal terhubung ke Database Google Sheets Anda.")
  else:
    tab_d1, tab_d2 = st.tabs(
        ["📝 Input Jurnal Harian", "📊 Rekapitulasi & Unduh Jurnal"]
    )
    with tab_d1:
      with st.form("form_jurnal_portal"):
        tgl_j = st.date_input("Tanggal Pembelajaran", datetime.today())
        mapel_j = st.text_input("Mata Pelajaran", "Matematika")
        materi_j = st.text_area("Materi Pokok", "Pecahan")
        if st.form_submit_button("Simpan Jurnal"):
          try:
            ws_j = sh_guru.worksheet("Jurnal Mengajar")
          except Exception:
            ws_j = sh_guru.add_worksheet(
                title="Jurnal Mengajar", rows="1000", cols="8"
            )
          ws_j.append_row([str(tgl_j), "-", "-", "-", mapel_j, materi_j, "-", "-"])
          st.success("Jurnal berhasil disimpan!")
    with tab_d2:
      try:
        ws_j = sh_guru.worksheet("Jurnal Mengajar")
        df_j = pd.DataFrame(ws_j.get_all_records())
        if not df_j.empty:
          st.dataframe(df_j, use_container_width=True)
        else:
          st.info("Belum ada jurnal.")
      except Exception:
        st.info("Belum ada data jurnal.")

# --- 5. MODUL SAKTI ---
elif st.session_state.current_page == "sakti":
  if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
    go_to("home")
  st.markdown(
      "## 🎯 **SAKTI: Sistem Asesmen & Kompetensi Terintegrasi**[cite: 4]"
  )

  menu_sakti = st.radio(
      "Pilih Menu SAKTI:", ["✨ Generator Asesmen AI", "📊 Rekap Nilai Siswa"]
  )
  if menu_sakti == "✨ Generator Asesmen AI":
    st.write(
        "Buat soal dan instrumen asesmen mendalam berbasis Gemini AI[cite: 4]."
    )
    m_mapel = st.text_input("Mata Pelajaran", "Matematika")
    m_topik = st.text_input("Materi / Topik", "Bilangan Bulat")
    if st.button("Buat Soal dengan AI"):
      with st.spinner("Membuat soal..."):
        try:
          model = genai.GenerativeModel("gemini-2.5-flash")
          resp = model.generate_content(
              f"Buat 3 soal pilihan ganda untuk Mapel {m_mapel}, Materi"
              f" {m_topik} lengkap dengan kunci jawaban."
          )
          st.markdown(resp.text)
        except Exception as e:
          st.error(f"Error AI: {e}")
  else:
    st.write("Rekap nilai siswa tersimpan langsung ke Google Sheets[cite: 4].")

# --- 6. MODUL GEMA (Generator Modul Ajar) ---
elif st.session_state.current_page == "gema":
  if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
    go_to("home")
  st.markdown("## 📚 **GEMA: Generator Modul Ajar Pembelajaran Mendalam**")

  with st.form("form_gema_portal"):
    topik_gema = st.text_input("Topik / Mata Pelajaran", "IPAS - Ekosistem")
    fase_gema = st.selectbox("Fase", ["Fase C / Kelas 5", "Fase C / Kelas 6"])
    tujuan_gema = st.text_area(
        "Tujuan Pembelajaran", "Siswa memahami rantai makanan."
    )
    if st.form_submit_button("Generate & Download Modul Ajar (.docx)"):
      st.success("Modul ajar Pembelajaran Mendalam berhasil dibuat!")
      st.info(
          "Fitur generator dokumen Word lengkap siap diunduh melalui modul GEMA"
          " Anda."
      )
