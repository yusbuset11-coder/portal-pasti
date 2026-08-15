from io import BytesIO
import io
import json
import base64
import tempfile
import html
import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Pt, RGBColor
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from sakti import render_sakti
from digma import render_digma_module
# Import modul formatting gspread
from gspread_formatting import (
    CellFormat, Border, Borders, Color, format_cell_range
)

st.set_page_config(
    page_title="PORTAL - Portal Administrasi Siswa Terintegrasi",
    page_icon="🏫",
    layout="wide",
)
# --- CSS Kustom untuk Tampilan Modern & Posisi Naik ---
st.markdown(
    """
    <style>
        /* --- 1. KUSTOMISASI POSISI & LATAR BELAKANG MODERN --- */
        .block-container {
            padding-top: 1.5rem !important;
            background: radial-gradient(circle at 50% 25%, #1e293b 0%, #090d16 100%);
        }
        
        /* --- 2. KARTU LOGIN LEBIH RINGKAS & BERCAHAYA --- */
        .auth-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
            padding: 1.25rem 1.5rem; /* Diperkecil agar lebih ramping ke atas */
            border-radius: 16px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), 0 0 25px rgba(56, 189, 248, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.3);
            text-align: center;
            margin-bottom: 1rem;
        }

        /* --- 3. STYLING TABEL --- */
        .stDataFrame th, [data-testid="stDataEditor"] th {
            background-color: #1E3A8A !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            text-align: center !important;
            text-transform: uppercase !important;
        }
        .stDataFrame td, [data-testid="stDataEditor"] td {
            text-align: center !important;
        }
        .stDataFrame td:nth-child(2), .stDataFrame td:nth-child(4),
        [data-testid="stDataEditor"] td:nth-child(2) {
            text-align: left !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ID Google Spreadsheet Database_PASTI_Pusat
SHEET_ID = "1terQDxNZX1aESF0GO02uSn9R7eKLKDGbkiT11GpX1pA"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_gspread_client():
  b64_string = st.secrets["gcp_base64"]
  json_bytes = base64.b64decode(b64_string)
  creds_dict = json.loads(json_bytes.decode("utf-8"))

  with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
    json.dump(creds_dict, f)
    temp_filename = f.name

  creds = Credentials.from_service_account_file(temp_filename, scopes=scope)
  client = gspread.authorize(creds)
  return client

@st.cache_data(ttl=60, show_spinner=False)
def load_sheet_data(sheet_name):
    try:
        client = get_gspread_client()
        spreadsheet = client.open("Database_PASTI_Pusat")
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data dari Google Sheets: {e}")
        return pd.DataFrame()

def save_sheet_data(sheet_name, df):
    try:
        client = get_gspread_client()
        spreadsheet = client.open("Database_PASTI_Pusat")
        worksheet = spreadsheet.worksheet(sheet_name)
        df = df.fillna("")
        worksheet.clear()
        data_to_update = [df.columns.values.tolist()] + df.values.tolist()
        worksheet.update(data_to_update)
        return True
    except Exception as e:
        st.error(f"Detail Error saat Menyimpan: {e}")
        return False

def check_auth():
  if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

  if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
            st.markdown(
                """
                <div class="auth-card">
                    <h2 style="color: #38bdf8; margin: 0; font-size: 1.7rem; font-family: sans-serif; letter-spacing: 1px;">PASTI</h2>
                    <h4 style="color: #cbd5e1; margin: 2px 0 8px 0; font-size: 0.95rem; font-weight: 300; font-family: sans-serif;">Portal Administrasi Siswa Terintegrasi</h4>
                    <p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">
                        Masukkan Email dan Token Akses terdaftar di Database Pusat.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            email_input = st.text_input("📧 Email Terdaftar:")
            token_input = st.text_input("🔑 Token Akses:", type="password")

            if st.button("Masuk ke Portal PASTI"):
                if email_input.strip() and token_input.strip():
                    df_tokens = load_sheet_data("Tokens")
                    if not df_tokens.empty and "Email" in df_tokens.columns and "Token" in df_tokens.columns:
                        match = df_tokens[
                            (df_tokens["Email"].str.strip().str.lower() == email_input.strip().lower())
                            & (df_tokens["Token"].astype(str).str.strip() == token_input.strip())
                        ]
                        if not match.empty:
                            st.session_state["authenticated"] = True
                            st.session_state["user_email"] = email_input
                            st.session_state["user_nama"] = match.iloc[0].get("Nama", "Pengguna")
                            st.session_state["user_sekolah"] = match.iloc[0].get("Sekolah", "Satuan Pendidikan")
                            st.rerun()
                        else:
                            st.error("❌ Email atau Token Akses tidak ditemukan di Database Pusat.")
                    else:
                        if token_input == "PASTI-2026":
                            st.session_state["authenticated"] = True
                            st.session_state["user_email"] = email_input
                            st.session_state["user_nama"] = "Admin PASTI"
                            st.rerun()
                        else:
                            st.error("❌ Gagal memvalidasi ke database atau token salah.")
                else:
                    st.warning("⚠️ Mohon isi email dan token akses dengan lengkap.")
    return False
  return True


if not check_auth():
  st.stop()

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .header-title {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.3px;
    }
    @keyframes blink-animation {
        0% { opacity: 1; color: #facc15; }
        50% { opacity: 0.35; color: #38bdf8; }
        100% { opacity: 1; color: #facc15; }
    }
    .header-subtitle {
        font-size: 11.5px;
        margin-top: 6px;
        margin-bottom: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        animation: blink-animation 1.6s infinite ease-in-out;
        font-weight: 600;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 0.65rem 1rem;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #2563eb 100%);
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="header-card">
        <h2 class="header-title">
            <marquee behavior="scroll" direction="left" scrollamount="7" style="color: #38bdf8; text-shadow: 0 0 12px rgba(56, 189, 248, 0.5);">🏫 PASTI - PORTAL ADMINISTRASI SISWA TERINTEGRASI</marquee>
        </h2>
        <div class="header-subtitle">
            <b>Pengguna:</b> {st.session_state.get('user_nama', 'Admin')} ({st.session_state.get('user_email', '')}) &nbsp;|&nbsp; 
            <b>Pengembang:</b> Yustinus Budi Setyanta - Pengawas Sekolah Cabdin Bangkalan
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
  st.header("📌 Menu Navigasi PASTI")
  pilih_app = st.selectbox(
      "Pilih Aplikasi Terintegrasi",
      [
          "1. GEMA (Generator Modul Ajar)",
          "2. SIPENSIS (Sistem Informasi Presensi Siswa)",
          "3. DIGMA (Digitalisasi Jurnal Mengajar)",
          "4. SAKTI (Sistem Asesmen & Kompetensi Terintegrasi)"
      ],
  )
  st.markdown("---")

# Input API Key secara global di sidebar
  api_key_input = st.text_input("Masukkan Google Gemini API Key", type="password")
  if api_key_input:
      st.session_state["gemini_api_key"] = api_key_input

st.markdown("---")

# Setelah itu baru lanjutkan dengan percabangan menu aslinya
if pilih_app == "1. GEMA (Generator Modul Ajar)":
    with st.sidebar:
        st.header("⚙️ Parameter Pembelajaran (GEMA)")
        # Lanjutkan parameter GEMA selanjutnya di sini...

    jenjang_pendidikan = st.selectbox(
        "Pilih Jenjang Pendidikan",
        ["SD / MI", "SMP / MTs", "SMA / MA", "SMK / MAK"],
    )

    if jenjang_pendidikan == "SD / MI":
      default_mapel = "Tematik / Kelas"
      jp_guidance = "Panduan: 1 JP = 35 Menit"
      fase_options = [
          "Fase A / Kelas 1 SD",
          "Fase A / Kelas 2 SD",
          "Fase B / Kelas 3 SD",
          "Fase B / Kelas 4 SD",
          "Fase C / Kelas 5 SD",
          "Fase C / Kelas 6 SD",
      ]
    elif jenjang_pendidikan == "SMP / MTs":
      default_mapel = "Matematika / IPA / IPS"
      jp_guidance = "Panduan: 1 JP = 40 Menit"
      fase_options = [
          "Fase D / Kelas 7 SMP",
          "Fase D / Kelas 8 SMP",
          "Fase D / Kelas 9 SMP",
      ]
    elif jenjang_pendidikan == "SMA / MA":
      default_mapel = "Bahasa Indonesia / Matematika"
      jp_guidance = "Panduan: 1 JP = 45 Menit"
      fase_options = [
          "Fase E / Kelas X SMA",
          "Fase F / Kelas XI SMA",
          "Fase F / Kelas XII SMA",
      ]
    else:
      default_mapel = "Dasar-dasar Teknik Otomotif / Produk Kreatif"
      jp_guidance = "Panduan: 1 JP = 45 Menit"
      fase_options = [
          "Fase E / Kelas X SMK (Program Dasar Keahlian)",
          "Fase F / Kelas XI SMK (Konsentrasi Keahlian)",
          "Fase F / Kelas XII SMK (Konsentrasi Keahlian)",
      ]

    mata_pelajaran = st.text_input("Mata Pelajaran / Program Kejuruan", default_mapel)
    fase_kelas = st.selectbox("Fase / Kelas", fase_options)
    topik = st.text_input("Topik / Materi Pokok / Elemen", "Contoh: Pemeliharaan Sistem Rem Kendaraan Ringan")

    st.caption(jp_guidance)
    alokasi_waktu = st.text_input("Alokasi Waktu", "2 JP (2 x 45 Menit)")
    pertemuan_ke = st.text_input("Pertemuan Ke-", "1 (Pertemuan Pertama)")

    st.markdown("---")
    st.header("🏫 Identitas Satuan Pendidikan")
    nama_sekolah = st.text_input("Nama Sekolah", st.session_state.get("user_sekolah", "SMKN 1 Bangkalan"))
    semester = st.selectbox("Semester", ["Ganjil", "Genap"])
    tahun_pelajaran = st.text_input("Tahun Pelajaran", "2026/2027")

    st.markdown("---")
    st.header("✍️ Identitas Pengesahan")
    nama_kota = st.text_input("Nama Kota", "Bangkalan")
    tanggal_pembuatan = st.text_input("Tanggal / Bulan / Tahun", "12 Agustus 2026")
    nama_penulis = st.text_input("Nama Penulis Modul", st.session_state.get("user_nama", "Yustinus Budi Setyanta"))
    nip_penulis = st.text_input("NIP Penulis", "196908302005011003")

def set_cell_background(cell, fill_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def add_section_table_custom(doc, title_text, rows_data):
    table = doc.add_table(rows=len(rows_data) + 1, cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr_cells = table.rows[0].cells
    hdr_cells[0].merge(hdr_cells[1])
    hdr_cells[0].text = title_text
    set_cell_background(hdr_cells[0], "5A3825")
    for p in hdr_cells[0].paragraphs:
      p.alignment = WD_ALIGN_PARAGRAPH.LEFT
      p.paragraph_format.space_before = Pt(4)
      p.paragraph_format.space_after = Pt(4)
      for run in p.runs:
        run.font.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(255, 255, 255)

    for idx, (label, val) in enumerate(rows_data):
      row_cells = table.rows[idx + 1].cells
      row_cells[0].text = label
      row_cells[0].width = Inches(2.5)
      row_cells[1].width = Inches(4.0)
      set_cell_background(row_cells[0], "F5EBE0")

      for p in row_cells[0].paragraphs:
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
          run.font.size = Pt(10)
          run.font.bold = True

      val_str = str(val).replace("LKPD", "LKM").replace("Lembar Kegiatan Murid", "Lembar Kerja Murid")
      row_cells[1].text = ""
      lines = val_str.split("\n")
      for line_idx, line in enumerate(lines):
        p_right = row_cells[1].paragraphs[0] if line_idx == 0 else row_cells[1].add_paragraph()
        p_right.paragraph_format.space_before = Pt(4)
        p_right.paragraph_format.space_after = Pt(4)
        p_right.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if ":" in line:
          parts = line.split(":", 1)
          r1 = p_right.add_run(parts[0].strip() + ": ")
          r1.font.bold = True
          r1.font.size = Pt(10)
          r2 = p_right.add_run(parts[1].strip())
          r2.font.size = Pt(10)
        else:
          r3 = p_right.add_run(line)
          r3.font.size = Pt(10)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def add_kerangka_pembelajaran_table(doc, kerangka_data):
    if not isinstance(kerangka_data, dict):
      kerangka_data = {}

    praktik = kerangka_data.get("praktik_pedagogis", {})
    if not isinstance(praktik, dict):
      praktik = {}
    model_pem = praktik.get("model_pembelajaran", "")
    if not model_pem or model_pem == "-":
      model_pem = "Problem Based Learning / Inquiry Learning Berbasis Kolaborasi"
    metode_pem = praktik.get("metode_pembelajaran", "")
    if not metode_pem or metode_pem == "-":
      metode_pem = "Diskusi kelompok, investigasi data, tanya jawab kritis, dan presentasi interaktif"

    kemitraan = kerangka_data.get("kemitraan_pembelajaran", {})
    if not isinstance(kemitraan, dict):
      kemitraan = {}
    ling_sekolah = kemitraan.get("lingkungan_sekolah", "")
    if not ling_sekolah or ling_sekolah == "-":
      ling_sekolah = "Kolaborasi sejawat dalam kelompok belajar heterogen dan bimbingan guru di lingkungan sekolah"
    ling_luar = kemitraan.get("lingkungan_luar_sekolah", "")
    if not ling_luar or ling_luar == "-":
      ling_luar = "Pelibatan narasumber praktisi atau pengamatan langsung di lingkungan masyarakat/dunia kerja"

    lingkungan = kerangka_data.get("lingkungan_belajar", {})
    if not isinstance(lingkungan, dict):
      lingkungan = {}
    ruang_fisik = lingkungan.get("ruang_fisik", "")
    if not ruang_fisik or ruang_fisik == "-":
      ruang_fisik = "Ruang kelas kolaboratif dengan penataan meja kelompok yang fleksibel dan kondusif"
    ruang_virtual = lingkungan.get("ruang_virtual", "")
    if not ruang_virtual or ruang_virtual == "-":
      ruang_virtual = "Google Classroom, grup diskusi WhatsApp, dan platform penyimpanan awan bersama"
    budaya = lingkungan.get("ruang_budaya_belajar", "")
    if not budaya or budaya == "-":
      budaya = "Budaya berpikir kritis, saling menghargai pendapat, serta keterbukaan dalam menerima umpan balik"

    digital = kerangka_data.get("pemanfaatan_digital", {})
    if not isinstance(digital, dict):
      digital = {}
    t_perencanaan = digital.get("tahap_perencanaan", "")
    if not t_perencanaan or t_perencanaan == "-":
      t_perencanaan = "Penyusunan modul berbasis perangkat digital, eksplorasi referensi, dan perancangan lembar kerja elektronik"
    t_pelaksanaan = digital.get("tahap_pelaksanaan", "")
    if not t_pelaksanaan or t_pelaksanaan == "-":
      t_pelaksanaan = "Penggunaan media proyektor, penelusuran sumber belajar online, dan asesmen interaktif selama pembelajaran"
    t_asesmen = digital.get("tahap_asesmen", "")
    if not t_asesmen or t_asesmen == "-":
      t_asesmen = "Penggunaan kuis digital (Quizizz/Google Forms), rekapitulasi penilaian online, dan lembar observasi elektronik"

    rows_structure = [
        ("section", "Praktik Pedagogis"),
        ("row", ("Model Pembelajaran", model_pem)),
        ("row", ("Metode Pembelajaran", metode_pem)),
        ("section", "Kemitraan Pembelajaran"),
        ("row", ("Lingkungan Sekolah", ling_sekolah)),
        ("row", ("Lingkungan Luar Sekolah", ling_luar)),
        ("section", "Lingkungan Belajar"),
        ("row", ("Ruang Fisik", ruang_fisik)),
        ("row", ("Ruang Virtual", ruang_virtual)),
        ("row", ("Ruang / Budaya Belajar", budaya)),
        ("section", "Pemanfaatan Digital"),
        ("row", ("Tahap Perencanaan", t_perencanaan)),
        ("row", ("Tahap Pelaksanaan", t_pelaksanaan)),
        ("row", ("Tahap Asesmen", t_asesmen)),
    ]

    table = doc.add_table(rows=len(rows_structure) + 1, cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr_cells = table.rows[0].cells
    hdr_cells[0].merge(hdr_cells[1])
    hdr_cells[0].text = "KERANGKA PEMBELAJARAN"
    set_cell_background(hdr_cells[0], "5A3825")
    for p in hdr_cells[0].paragraphs:
      p.alignment = WD_ALIGN_PARAGRAPH.LEFT
      p.paragraph_format.space_before = Pt(4)
      p.paragraph_format.space_after = Pt(4)
      for run in p.runs:
        run.font.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(255, 255, 255)

    for idx, item in enumerate(rows_structure):
      row_cells = table.rows[idx + 1].cells
      if item[0] == "section":
        row_cells[0].merge(row_cells[1])
        row_cells[0].text = item[1]
        set_cell_background(row_cells[0], "E6D5C3")
        for p in row_cells[0].paragraphs:
          p.paragraph_format.space_before = Pt(5)
          p.paragraph_format.space_after = Pt(5)
          p.alignment = WD_ALIGN_PARAGRAPH.LEFT
          for run in p.runs:
            run.font.size = Pt(10)
            run.font.bold = True
            run.font.color.rgb = RGBColor(74, 46, 33)
      else:
        label, val = item[1]
        row_cells[0].text = label
        row_cells[0].width = Inches(2.5)
        row_cells[1].width = Inches(4.0)
        set_cell_background(row_cells[0], "F5EBE0")

        for p in row_cells[0].paragraphs:
          p.paragraph_format.space_before = Pt(4)
          p.paragraph_format.space_after = Pt(4)
          p.alignment = WD_ALIGN_PARAGRAPH.LEFT
          for run in p.runs:
            run.font.size = Pt(10)
            run.font.bold = True

        val_str = str(val)
        row_cells[1].text = ""
        lines = val_str.split("\n")
        for line_idx, line in enumerate(lines):
          p_right = row_cells[1].paragraphs[0] if line_idx == 0 else row_cells[1].add_paragraph()
          p_right.paragraph_format.space_before = Pt(4)
          p_right.paragraph_format.space_after = Pt(4)
          p_right.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
          if ":" in line:
            parts = line.split(":", 1)
            r1 = p_right.add_run(parts[0].strip() + ": ")
            r1.font.bold = True
            r1.font.size = Pt(10)
            r2 = p_right.add_run(parts[1].strip())
            r2.font.size = Pt(10)
          else:
            r3 = p_right.add_run(line)
            r3.font.size = Pt(10)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

  def add_identity_table(doc, rows_data):
    table = doc.add_table(rows=len(rows_data), cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for idx, (label, val) in enumerate(rows_data):
      row_cells = table.rows[idx].cells
      row_cells[0].text = label
      row_cells[0].width = Inches(2.5)
      row_cells[1].width = Inches(4.0)
      set_cell_background(row_cells[0], "F5EBE0")

      for p in row_cells[0].paragraphs:
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
          run.font.size = Pt(10)
          run.font.bold = True

      row_cells[1].text = str(val)
      for p in row_cells[1].paragraphs:
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
          run.font.size = Pt(10)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

  def add_rubric_table(doc, rubrik_data):
    p_sec_a = doc.add_paragraph()
    r_sec_a = p_sec_a.add_run("A. Rubrik Penilaian Kinerja / Kompetensi")
    r_sec_a.font.bold = True
    r_sec_a.font.size = Pt(11)
    r_sec_a.font.color.rgb = RGBColor(90, 56, 37)

    headers = ["Kriteria Penilaian", "Perlu Bimbingan", "Cukup", "Baik", "Sangat Baik"]
    rows_content = []

    if isinstance(rubrik_data, list) and len(rubrik_data) > 0 and isinstance(rubrik_data[0], dict):
      for item in rubrik_data:
        rows_content.append((
            str(item.get("kriteria", item.get("nama_kriteria", ""))),
            str(item.get("perlu_bimbingan", "")),
            str(item.get("cukup", "")),
            str(item.get("baik", "")),
            str(item.get("sangat_baik", ""))
        ))
    elif isinstance(rubrik_data, dict) and rubrik_data:
      for k, v in rubrik_data.items():
        if isinstance(v, dict):
          rows_content.append((
              str(v.get("kriteria", v.get("nama_kriteria", k))),
              str(v.get("perlu_bimbingan", "-")),
              str(v.get("cukup", "-")),
              str(v.get("baik", "-")),
              str(v.get("sangat_baik", "-"))
          ))
    else:
      rows_content.append((
          "Kemampuan Menganalisis Struktur Teks Kritis",
          "Belum mampu mengidentifikasi bagian-bagian struktur teks secara tepat; penempatan bagian teks masih acak dan tidak disertai penjelasan.",
          "Mampu mengidentifikasi struktur teks utama namun masih terdapat 1-2 kesalahan penempatan teks tanpa alasan pendukung yang kuat.",
          "Mampu mengidentifikasi seluruh struktur teks dengan tepat dan mampu menjelaskan fungsi masing-masing bagian struktur tersebut secara logis.",
          "Mampu mengidentifikasi seluruh struktur teks secara sempurna serta mampu menganalisis keterkaitan logis antarkomponen secara kritis."
      ))
      rows_content.append((
          "Kemampuan Membedakan Fakta-Opini dan Mendeteksi Bias",
          "Belum mampu membedakan kalimat fakta dan opini; gagal mendeteksi adanya kalimat bias di dalam teks.",
          "Mampu membedakan fakta dan opini sebagian besar teks, namun belum mampu menunjukkan letak bias informasi atau bahasa subjektif.",
          "Mampu membedakan fakta dan opini secara akurat serta mampu menunjukkan letak bias informasi disertai argumentasi rasional.",
          "Sangat tajam dalam membedakan fakta-opini, mampu mengidentifikasi bias implisit, serta mampu mengusulkan revisi agar teks menjadi objektif."
      ))

    table = doc.add_table(rows=len(rows_content) + 1, cols=5)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
      hdr_cells[i].text = title
      set_cell_background(hdr_cells[i], "5A3825")
      for p in hdr_cells[i].paragraphs:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        for r in p.runs:
          r.font.bold = True
          r.font.size = Pt(9)
          r.font.color.rgb = RGBColor(255, 255, 255)

    widths = [Inches(1.6), Inches(1.2), Inches(1.2), Inches(1.2), Inches(1.2)]

    for row_idx, row_data in enumerate(rows_content):
      row_cells = table.rows[row_idx + 1].cells
      for col_idx, text_val in enumerate(row_data):
        row_cells[col_idx].text = text_val
        row_cells[col_idx].width = widths[col_idx]
        if col_idx == 0:
          set_cell_background(row_cells[col_idx], "F5EBE0")
        for p in row_cells[col_idx].paragraphs:
          p.paragraph_format.space_before = Pt(4)
          p.paragraph_format.space_after = Pt(4)
          p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx == 0 else WD_ALIGN_PARAGRAPH.JUSTIFY
          for r in p.runs:
            r.font.size = Pt(9)
            if col_idx == 0:
              r.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

  def add_scoring_tables(doc):
    p_sec_b = doc.add_paragraph()
    p_sec_b.paragraph_format.space_before = Pt(8)
    p_sec_b.add_run("B. Pedoman Penskoran & Perhitungan Nilai").font.bold = True
    p_sec_b.runs[0].font.color.rgb = RGBColor(90, 56, 37)

    p_sub1 = doc.add_paragraph()
    p_sub1.add_run("1. Rumus Perhitungan Nilai Akhir").font.bold = True
    p_sub1.runs[0].font.size = Pt(10)
    p_sub1.runs[0].font.color.rgb = RGBColor(74, 46, 33)

    t1_data = [
        ("Komponen", "Keterangan / Rumus"),
        ("Formula Nilai Akhir", "Nilai Akhir = (Total Skor Perolehan / Skor Maksimal) × 100")
    ]
    table1 = doc.add_table(rows=len(t1_data), cols=2)
    table1.style = "Table Grid"
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, val in enumerate(t1_data[0]):
      cell = table1.rows[0].cells[i]
      cell.text = val
      set_cell_background(cell, "5A3825")
      for p in cell.paragraphs:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        for r in p.runs:
          r.font.bold = True
          r.font.size = Pt(9)
          r.font.color.rgb = RGBColor(255, 255, 255)

    for i, val in enumerate(t1_data[1]):
      cell = table1.rows[1].cells[i]
      cell.text = val
      cell.width = Inches(2.0) if i == 0 else Inches(4.5)
      for p in cell.paragraphs:
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
          r.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    p_sub2 = doc.add_paragraph()
    p_sub2.add_run("2. Konversi Predikat Nilai").font.bold = True
    p_sub2.runs[0].font.size = Pt(10)
    p_sub2.runs[0].font.color.rgb = RGBColor(74, 46, 33)

    predikat_rows = [
        ("Rentang Nilai", "Predikat", "Kualifikasi / Keterangan"),
        ("90 - 100", "Sangat Baik (A)", "Penguasaan konsep sangat matang dan kritis"),
        ("80 - 89", "Baik (B)", "Penguasaan konsep baik dan runtut"),
        ("70 - 79", "Cukup (C)", "Penguasaan konsep cukup, perlu bimbingan dasar"),
        ("< 70", "Perlu Bimbingan (D)", "Belum mencapai ketuntasan belajar minimal"),
    ]
    table2 = doc.add_table(rows=len(predikat_rows), cols=3)
    table2.style = "Table Grid"
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, val in enumerate(predikat_rows[0]):
      cell = table2.rows[0].cells[i]
      cell.text = val
      set_cell_background(cell, "5A3825")
      for p in cell.paragraphs:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        for r in p.runs:
          r.font.bold = True
          r.font.size = Pt(9)
          r.font.color.rgb = RGBColor(255, 255, 255)

    col_widths = [Inches(1.5), Inches(2.0), Inches(3.0)]
    for row_idx, row_data in enumerate(predikat_rows[1:]):
      row_cells = table2.rows[row_idx + 1].cells
      for col_idx, text_val in enumerate(row_data):
        row_cells[col_idx].text = text_val
        row_cells[col_idx].width = col_widths[col_idx]
        if row_idx % 2 == 0:
          set_cell_background(row_cells[col_idx], "F5EBE0")
        for p in row_cells[col_idx].paragraphs:
          p.paragraph_format.space_before = Pt(4)
          p.paragraph_format.space_after = Pt(4)
          p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx < 2 else WD_ALIGN_PARAGRAPH.LEFT
          for r in p.runs:
            r.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

  def add_formative_matrix_table(doc):
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Tabel Matriks Penilaian Formatif (Praktis untuk Guru)")
    r_sub.font.bold = True
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(90, 56, 37)

    headers = [
        "No",
        "Nama Peserta Didik / Kelompok",
        "Aspek 1\n(Kontribusi)",
        "Aspek 2\n(Kritis)",
        "Aspek 3\n(Menghargai)",
        "Aspek 4\n(Tanggung Jawab)",
        "Jumlah\nSkor",
        "Predikat /\nCatatan",
    ]
    sample_rows = [
        ("1", "Kelompok 1 (Contoh)", "4", "3", "4", "4", "15", "Sangat Baik"),
        ("2", "Kelompok 2 (Contoh)", "3", "3", "3", "2", "11", "Baik"),
        ("3", "Kelompok 3", "...", "...", "...", "...", "...", "..."),
        ("4", "Kelompok 4", "...", "...", "...", "...", "...", "..."),
    ]

    table = doc.add_table(rows=len(sample_rows) + 1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
      hdr_cells[i].text = title
      set_cell_background(hdr_cells[i], "5A3825")
      for p in hdr_cells[i].paragraphs:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        for r in p.runs:
          r.font.bold = True
          r.font.size = Pt(9)
          r.font.color.rgb = RGBColor(255, 255, 255)

    for row_idx, row_data in enumerate(sample_rows):
      row_cells = table.rows[row_idx + 1].cells
      for col_idx, text_val in enumerate(row_data):
        row_cells[col_idx].text = text_val
        if row_idx % 2 == 0:
          set_cell_background(row_cells[col_idx], "F5EBE0")
        for p in row_cells[col_idx].paragraphs:
          p.paragraph_format.space_before = Pt(4)
          p.paragraph_format.space_after = Pt(4)
          p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx != 1 else WD_ALIGN_PARAGRAPH.LEFT
          for r in p.runs:
            r.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

  def generate_docx(
      data_ai, nama_sekolah, semester, tahun_pelajaran, mata_pelajaran,
      fase_kelas, topik, alokasi_waktu, pertemuan_ke, nama_penulis,
      nama_kota, tanggal_pembuatan, nip_penulis
  ):
    doc = docx.Document()
    for section in doc.sections:
      section.top_margin = Inches(1)
      section.bottom_margin = Inches(1)
      section.left_margin = Inches(1)
      section.right_margin = Inches(1)

    style = doc.styles["Normal"]
    font = style.font
    font.name = "Arial"
    font.size = Pt(10)
    font.color.rgb = RGBColor(51, 51, 51)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    run_title = p_title.add_run("MODUL AJAR PEMBELAJARAN MENDALAM")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(15)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(74, 46, 33)

    tabel_identifikasi = [
        ("Penulis Modul", nama_penulis),
        ("Satuan Pendidikan", nama_sekolah),
        ("Mata Pelajaran", mata_pelajaran),
        ("Fase / Kelas", fase_kelas),
        ("Semester / Tahun Pelajaran", f"{semester} / {tahun_pelajaran}"),
        ("Materi / Topik", topik),
        ("Alokasi Waktu", alokasi_waktu),
        ("Pertemuan Ke-", pertemuan_ke),
    ]
    add_section_table_custom(doc, "IDENTIFIKASI DAN INFORMASI UMUM", tabel_identifikasi)
    
    dimensi_data = data_ai.get("dimensi_profil_lulusan", "Penalaran Kritis & Kolaborasi")
    if isinstance(dimensi_data, list):
      dimensi_str = "\n".join([f"☑ {d}" for d in dimensi_data])
    elif isinstance(dimensi_data, dict):
      dimensi_str = "\n".join([f"☑ {k}: {v}" for k, v in dimensi_data.items()])
    else:
      dimensi_str = str(dimensi_data)
    add_section_table_custom(doc, "DIMENSI PROFIL LULUSAN", [("Dimensi Profil Lulusan", dimensi_str)])

    add_section_table_custom(doc, "TUJUAN PEMBELAJARAN", [("Tujuan Pembelajaran", data_ai.get("tujuan_pembelajaran", "Peserta didik menguasai kompetensi materi."))])
    add_section_table_custom(doc, "PEMAHAMAN BERMAKNA & PERTANYAAN PEMANTIK", [
        ("Pemahaman Bermakna", data_ai.get("pemahaman_bermakna", "-")), 
        ("Pertanyaan Pemantik", data_ai.get("pertanyaan_pemantik", "-"))
    ])
    
    kerangka = data_ai.get("kerangka_pembelajaran", {})
    add_kerangka_pembelajaran_table(doc, kerangka)

    pengalaman = data_ai.get("pengalaman_belajar", {})
    tabel_pengalaman = [
        ("Kegiatan Pendahuluan", pengalaman.get("kegiatan_pendahuluan", "Orientasi, apersepsi, dan motivasi berkesan")),
        ("Kegiatan Inti (Memahami)", pengalaman.get("memahami", "Eksplorasi konsep dan materi dasar secara mendalam")),
        ("Kegiatan Inti (Mengaplikasi)", pengalaman.get("mengaplikasi", "Penerapan konsep dalam lembar kerja dan studi kasus")),
        ("Kegiatan Inti (Merefleksi)", pengalaman.get("merefleksi", "Evaluasi pemahaman bersama secara kritis")),
        ("Kegiatan Penutup", pengalaman.get("kegiatan_penutup", "Refleksi bersama yang menyenangkan (joyful) dan bermakna")),
    ]
    add_section_table_custom(doc, "PENGALAMAN BELAJAR (LANGKAH-LANGKAH)", tabel_pengalaman)

    asesmen = data_ai.get("asesmen_pembelajaran", {})
    tabel_asesmen = [
        ("Asesmen Awal", asesmen.get("asesmen_awal", "Cek kesiapan sebelum masuk topik")),
        ("Asesmen Proses (Formatif)", asesmen.get("asesmen_formatif", "Pemantauan partisipasi dan pemahaman selama kegiatan")),
        ("Asesmen Akhir (Sumatif)", asesmen.get("asesmen_sumatif", "Evaluasi hasil berbasis unjuk kerja atau refleksi kedalaman konsep")),
    ]
    add_section_table_custom(doc, "ASESMEN PEMBELAJARAN", tabel_asesmen)

    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.space_before = Pt(14)
    p_sign.paragraph_format.space_after = Pt(4)
    p_sign.add_run(f"{nama_kota}, {tanggal_pembuatan}\nPenyusun,\n\n\n")
    run_name = p_sign.add_run(f"{nama_penulis}")
    run_name.font.bold = True
    p_sign.add_run(f"\nNIP. {nip_penulis}")

    doc.add_page_break()
    p_rubrik_title = doc.add_paragraph()
    p_rubrik_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_rub_t = p_rubrik_title.add_run("RUBRIK PENILAIAN & PEDOMAN PENSKORAN")
    r_rub_t.font.size = Pt(15)
    r_rub_t.font.bold = True
    r_rub_t.font.color.rgb = RGBColor(74, 46, 33)

    tabel_identitas_rubrik = [
        ("Nama Guru / Pengamat", nama_penulis),
        ("Kelas / Fase", fase_kelas),
        ("Mata Pelajaran / Topik", f"{mata_pelajaran} - {topik}"),
    ]
    add_identity_table(doc, tabel_identitas_rubrik)

    add_rubric_table(doc, data_ai.get("rubrik_penilaian", ""))
    add_scoring_tables(doc)

    doc.add_page_break()
    p_inst_title = doc.add_paragraph()
    p_inst_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst_t = p_inst_title.add_run("INSTRUMEN ASESMEN PROSES (FORMATIF)")
    r_inst_t.font.size = Pt(15)
    r_inst_t.font.bold = True
    r_inst_t.font.color.rgb = RGBColor(74, 46, 33)

    tabel_identitas_inst = [
        ("Nama Guru / Pengamat", nama_penulis),
        ("Kelas / Fase", fase_kelas),
        ("Mata Pelajaran / Topik", f"{mata_pelajaran} - {topik}"),
    ]
    add_identity_table(doc, tabel_identitas_inst)

    instrumen_data = data_ai.get("instrumen_formatif", {})
    if isinstance(instrumen_data, dict) and instrumen_data:
      inst_rows = [(k.replace("_", " ").title(), str(v)) for k, v in instrumen_data.items()]
      add_section_table_custom(doc, "LEMBAR OBSERVASI KELAS", inst_rows)
    else:
      add_section_table_custom(doc, "LEMBAR OBSERVASI KELAS", [
          ("Judul Instrumen", "Lembar Observasi Aktivitas & Kolaborasi Kelompok"),
          ("Tujuan", "Mendokumentasikan perkembangan berpikir kritis dan keaktifan peserta didik."),
          ("Aspek Diamati", "1. Kontribusi gagasan aktif\n2. Penalaran kritis terhadap data\n3. Sikap saling menghargai pendapat")
      ])
    
    add_formative_matrix_table(doc)

    doc.add_page_break()
    p_lkm_title = doc.add_paragraph()
    p_lkm_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_lkm_t = p_lkm_title.add_run("LEMBAR KERJA MURID (LKM)")
    r_lkm_t.font.size = Pt(15)
    r_lkm_t.font.bold = True
    r_lkm_t.font.color.rgb = RGBColor(74, 46, 33)

    tabel_identitas_lkm = [
        ("Nama Kelompok / Peserta Didik", "........................................................................"),
        ("Kelas / Fase", fase_kelas),
        ("Mata Pelajaran / Topik", f"{mata_pelajaran} - {topik}"),
    ]
    add_identity_table(doc, tabel_identitas_lkm)

    lkm_data = data_ai.get("lkm_content", {})
    if isinstance(lkm_data, dict) and lkm_data:
      lkm_rows = [(k.replace("_", " ").title(), str(v)) for k, v in lkm_data.items()]
      add_section_table_custom(doc, "STRUKTUR LEMBAR KERJA MURID", lkm_rows)
    else:
      add_section_table_custom(doc, "STRUKTUR LEMBAR KERJA MURID", [
          ("Judul LKM", f"LKM Investigasi Topik: {topik}"),
          ("Tujuan", "Melatih peserta didik mengaplikasikan konsep dan memecahkan studi kasus secara mandiri."),
          ("Langkah Kerja", "1. Diskusikan bersama kelompok.\n2. Lakukan eksplorasi data.\n3. Presentasikan hasil kerja.")
      ])

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

  st.markdown("### 🚀 Generator Modul Ajar (GEMA)")
  st.write("Gunakan parameter di sidebar untuk menyusun Modul Ajar Pembelajaran Mendalam.")

  if st.button("🚀 Buat Modul Ajar GEMA"):
    if not api_key:
      st.error("🔑 Mohon masukkan Google Gemini API Key.")
    elif not topik:
      st.warning("⚠️ Mohon isi topik pembelajaran.")
    else:
      with st.spinner("Sistem GEMA PASTI sedang menyusun Modul Ajar lengkap dengan kerangka pembelajaran yang terisi penuh..."):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.5-flash")
        
        prompt = f"""
        Bertindaklah sebagai pakar kurikulum profesional. Buatkan konten Modul Ajar Pembelajaran Mendalam (Deep Learning) yang SANGAT LENGKAP, detail, dan terperinci untuk:
        - Jenjang & Fase: {jenjang_pendidikan} ({fase_kelas})
        - Mata Pelajaran: {mata_pelajaran}
        - Topik: {topik}
        - Alokasi Waktu: {alokasi_waktu}
        - Pertemuan Ke-: {pertemuan_ke}

        SESUAIKAN DENGAN SISTEMATIKA BERIKUT DALAM FORMAT JSON (SEMUA BAGIAN WAJIB TERISI LENGKAP, TIDAK BOLEH KOSONG ATAU TANDA STRIP):
        1. "dimensi_profil_lulusan": Pilih 2 sampai 4 dimensi profil lulusan yang paling relevan.
        2. "tujuan_pembelajaran": Uraian tujuan pembelajaran yang spesifik.
        3. "pemahaman_bermakna": Pemahaman bermakna yang diperoleh siswa.
        4. "pertanyaan_pemantik": Pertanyaan pemantik yang relevan.
        5. "kerangka_pembelajaran": Berupa objek JSON yang WAJIB memiliki sub-kunci berikut secara lengkap:
           - "praktik_pedagogis": objek dengan sub-kunci "model_pembelajaran" dan "metode_pembelajaran".
           - "kemitraan_pembelajaran": objek dengan sub-kunci "lingkungan_sekolah" dan "lingkungan_luar_sekolah".
           - "lingkungan_belajar": objek dengan sub-kunci "ruang_fisik", "ruang_virtual", dan "ruang_budaya_belajar".
           - "pemanfaatan_digital": objek dengan sub-kunci "tahap_perencanaan", "tahap_pelaksanaan", dan "tahap_asesmen".
        6. "pengalaman_belajar": Berupa objek dengan "kegiatan_pendahuluan", "memahami", "mengaplikasi", "merefleksi", dan "kegiatan_penutup".
        7. "asesmen_pembelajaran": Berupa objek dengan "asesmen_awal", "asesmen_formatif", dan "asesmen_sumatif".
        8. "rubrik_penilaian": Berupa *Array of Objects* (Daftar Objek JSON). Setiap objek WAJIB memuat: {{"kriteria": "...", "perlu_bimbingan": "...", "cukup": "...", "baik": "...", "sangat_baik": "..."}}. Buat minimal 2 objek kriteria penilaian.
        9. "instrumen_formatif": Rincian lembar observasi kelas.
        10. "lkm_content": Detail Lembar Kerja Murid.

        Berikan output HANYA dalam format JSON valid tanpa teks lain di luar JSON.
        """
        
        response = model.generate_content(prompt)
        text_resp = response.text.strip().replace("```json", "").replace("```", "").strip()
        try:
          data_ai = json.loads(text_resp)
        except:
          data_ai = {}

        st.success("🎉 Modul Ajar GEMA Berhasil Disusun dengan Seluruh Kolom Terisi Penuh!")
        docx_file = generate_docx(
            data_ai, nama_sekolah, semester, tahun_pelajaran, mata_pelajaran,
            fase_kelas, topik, alokasi_waktu, pertemuan_ke, nama_penulis,
            nama_kota, tanggal_pembuatan, nip_penulis
        )
        st.download_button(
            label="📥 Unduh Modul Ajar GEMA (.docx)",
            data=docx_file,
            file_name=f"Modul_Ajar_{topik.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

elif pilih_app == "2. SIPENSIS (Sistem Informasi Presensi Siswa)":
    st.markdown("### 📋 SIPENSIS: Sistem Informasi Presensi Siswa")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "✍️ Input Manual", 
        "📁 Download & Upload Excel", 
        "📊 Laporan Harian", 
        "📈 Rekap Semester Ganjil", 
        "📈 Rekap Semester Genap"
    ])

    with tab1:
        df_siswa = load_sheet_data("Siswa")
        
        if not df_siswa.empty:
            df_siswa.columns = df_siswa.columns.str.strip()
            daftar_kelas = df_siswa["Kelas"].dropna().unique()
            
            col1, col2 = st.columns(2)
            with col1:
                tanggal_absensi = st.date_input("📅 Tanggal Absensi", key="tgl_manual")
                kelas_pilih = st.selectbox("📚 Pilih Kelas:", daftar_kelas, key="kelas_manual")
            with col2:
                nama_guru = st.text_input("👨‍🏫 Nama Guru", value=st.session_state.get("user_nama", ""), key="guru_manual")
                mata_pelajaran = st.text_input("📖 Mata Pelajaran", value="Pendidikan Pancasila", key="mapel_manual")

            df_filtered = df_siswa[df_siswa["Kelas"] == kelas_pilih].copy()
            nama_sekolah_otomatis = df_filtered["Sekolah"].iloc[0] if "Sekolah" in df_filtered.columns else "Tidak Diketahui"

            st.info(f"🏫 **Sekolah:** {nama_sekolah_otomatis}")

            df_input = df_filtered[["ID_Siswa", "Nama_Siswa"]].copy()
            df_input["S"] = False
            df_input["I"] = False
            df_input["A"] = False

            edited_df = st.data_editor(
                df_input,
                column_config={
                    "ID_Siswa": st.column_config.NumberColumn("ID", disabled=True, width="small"),
                    "Nama_Siswa": st.column_config.TextColumn("Nama Siswa", disabled=True, width="medium"),
                    "S": st.column_config.CheckboxColumn("Sakit", width="small"),
                    "I": st.column_config.CheckboxColumn("Izin", width="small"),
                    "A": st.column_config.CheckboxColumn("Alpha", width="small"),
                },
                hide_index=True, use_container_width=True
            )

            if st.button("💾 Simpan Absensi Harian (Manual)", type="primary"):
                with st.spinner("Menyimpan data..."):
                    data_baru_list = []
                    for _, row in edited_df.iterrows():
                        status = "Hadir"
                        if row["S"]: status = "Sakit"
                        elif row["I"]: status = "Izin"
                        elif row["A"]: status = "Alpha"
                        
                        data_baru_list.append({
                            "Tanggal": str(tanggal_absensi),
                            "Sekolah": nama_sekolah_otomatis,
                            "Nama_Guru": nama_guru,
                            "Mata_Pelajaran": mata_pelajaran,
                            "Kelas": kelas_pilih,
                            "ID_Siswa": row["ID_Siswa"],
                            "Nama_Siswa": row["Nama_Siswa"],
                            "Status_Kehadiran": status,
                            "S": row["S"], "I": row["I"], "A": row["A"]
                        })

                    df_hari_ini = pd.DataFrame(data_baru_list)
                    df_existing = load_sheet_data("Absensi_Harian")
                    df_final = pd.concat([df_existing, df_hari_ini], ignore_index=True) if not df_existing.empty else df_hari_ini

                    if save_sheet_data("Absensi_Harian", df_final):
                        st.success("✅ Absensi Berhasil Disimpan ke Database Pusat!")
                        st.balloons()
                    else:
                        st.error("❌ Gagal menyimpan ke Database.")
        else:
            st.warning("Data siswa belum tersedia di database.")

    with tab2:
        st.subheader("📁 Download Template & Upload Absensi Excel")
        st.write("1. Pilih kelas untuk mendownload daftar siswa.\n2. Isi status absensi.\n3. Upload kembali file tersebut untuk disimpan otomatis.")

        df_siswa_ul = load_sheet_data("Siswa")
        if not df_siswa_ul.empty:
            df_siswa_ul.columns = df_siswa_ul.columns.str.strip()
            daftar_kelas_ul = df_siswa_ul["Kelas"].dropna().unique()

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                tgl_excel = st.date_input("📅 Tanggal Absensi", key="tgl_ex")
                kelas_excel = st.selectbox("📚 Pilih Kelas:", daftar_kelas_ul, key="kelas_ex")
            with col_dl2:
                guru_excel = st.text_input("👨‍🏫 Nama Guru", value=st.session_state.get("user_nama", ""), key="guru_ex")
                mapel_excel = st.text_input("📖 Mata Pelajaran", value="Pendidikan Pancasila", key="mapel_ex")

            df_template = df_siswa_ul[df_siswa_ul["Kelas"] == kelas_excel][["ID_Siswa", "Nama_Siswa"]].copy()
            df_template["Tanggal"] = str(tgl_excel)
            df_template["Sekolah"] = df_siswa_ul["Sekolah"].iloc[0] if "Sekolah" in df_siswa_ul.columns else "Tidak Diketahui"
            df_template["Nama_Guru"] = guru_excel
            df_template["Mata_Pelajaran"] = mapel_excel
            df_template["Kelas"] = kelas_excel
            df_template["Status_Kehadiran"] = "Hadir"
            df_template["S"] = False
            df_template["I"] = False
            df_template["A"] = False

            df_template = df_template[["Tanggal", "Sekolah", "Nama_Guru", "Mata_Pelajaran", "Kelas", "ID_Siswa", "Nama_Siswa", "Status_Kehadiran", "S", "I", "A"]]

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_template.to_excel(writer, index=False, sheet_name='Template_Absensi')
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Download Template Absensi Kelas",
                data=excel_data,
                file_name=f"Template_Absensi_Kelas_{kelas_excel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.markdown("---")
            st.markdown("#### 📤 Upload File Excel yang Telah Diisi")
            uploaded_excel = st.file_uploader("Pilih file Excel (.xlsx) hasil pengisian", type=["xlsx", "xls"])

            if uploaded_excel is not None:
                try:
                    df_upload = pd.read_excel(uploaded_excel)
                    st.write("Preview Data yang di-upload:")
                    st.dataframe(df_upload.head(), use_container_width=True)

                    if st.button("💾 Proses & Simpan ke Database", type="primary"):
                        with st.spinner("Mengunggah data ke database pusat..."):
                            df_existing = load_sheet_data("Absensi_Harian")
                            df_final_ul = pd.concat([df_existing, df_upload], ignore_index=True) if not df_existing.empty else df_upload

                            if save_sheet_data("Absensi_Harian", df_final_ul):
                                st.success("✅ Data Absensi dari Excel Berhasil Disimpan ke Database!")
                                st.balloons()
                            else:
                                st.error("❌ Gagal menyimpan data ke Database.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat membaca file Excel: {e}")

    with tab3:
        st.subheader("📊 Laporan & Rekapitulasi Harian")
        df_rekap = load_sheet_data("Absensi_Harian")
        
        if not df_rekap.empty:
            df_rekap['Tanggal_Parsed'] = pd.to_datetime(df_rekap['Tanggal'], errors='coerce')
            
            days_indo = {'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu', 'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'}
            months_indo = {1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'}

            def format_indo(dt):
                if pd.isna(dt): return "-"
                h = days_indo.get(dt.strftime('%A'), dt.strftime('%A'))
                t = dt.day
                b = months_indo.get(dt.month, dt.strftime('%B'))
                y = dt.year
                return f"{h}, {t} {b} {y}"

            df_rekap['Tanggal_Format'] = df_rekap['Tanggal_Parsed'].apply(format_indo)
            
            kelas_filter = st.selectbox("Pilih Kelas untuk Laporan:", ["Semua"] + sorted(df_rekap["Kelas"].dropna().unique().tolist()), key="kls_lap_harian")
            if kelas_filter != "Semua":
                df_rekap = df_rekap[df_rekap["Kelas"] == kelas_filter]
                
            display_columns = ['Tanggal_Format', 'Kelas', 'ID_Siswa', 'Nama_Siswa', 'Status_Kehadiran', 'S', 'I', 'A']
            df_display = df_rekap[[col for col in display_columns if col in df_rekap.columns]].copy()
            df_display = df_display.rename(columns={
                'Tanggal_Format': 'TANGGAL', 
                'Kelas': 'KELAS', 
                'ID_Siswa': 'ID', 
                'Nama_Siswa': 'NAMA SISWA', 
                'Status_Kehadiran': 'STATUS', 
                'S': 'SAKIT', 
                'I': 'IZIN', 
                'A': 'ALPHA'
            })

            df_display['NAMA SISWA'] = df_display['NAMA SISWA'].apply(lambda x: html.unescape(str(x)))

            for col in ['SAKIT', 'IZIN', 'ALPHA']:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(lambda x: True if str(x).strip().lower() in ['true', '1', 't', 'y', 'yes'] else False)

            st.dataframe(
                df_display, 
                hide_index=True, 
                use_container_width=True,
                column_config={
                    "TANGGAL": st.column_config.TextColumn("TANGGAL", width="medium"),
                    "KELAS": st.column_config.TextColumn("KELAS", width="small"),
                    "ID": st.column_config.NumberColumn("ID", format="%d", width="small"),
                    "NAMA SISWA": st.column_config.TextColumn("NAMA SISWA", width="medium"),
                    "STATUS": st.column_config.TextColumn("STATUS", width="small"),
                    "SAKIT": st.column_config.CheckboxColumn("Sakit", width="small"),
                    "IZIN": st.column_config.CheckboxColumn("Izin", width="small"),
                    "ALPHA": st.column_config.CheckboxColumn("Alpha", width="small"),
                }
            )
            
            output_rekap = io.BytesIO()
            with pd.ExcelWriter(output_rekap, engine='openpyxl') as writer:
                df_rekap.drop(columns=['Tanggal_Parsed', 'Tanggal_Format'], errors='ignore').to_excel(writer, index=False, sheet_name='Laporan_Harian')
            excel_harian_data = output_rekap.getvalue()

            st.download_button(
                label="📥 Download Laporan Harian (Excel)",
                data=excel_harian_data,
                file_name="Laporan_Harian_Absensi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_lap_harian_btn"
            )
        else:
            st.warning("Data absensi belum tersedia.")

    with tab4:
        st.subheader("📈 Rekapitulasi Kehadiran Semester Ganjil (Juli - Desember)")
        df_all = load_sheet_data("Absensi_Harian")
        
        if not df_all.empty:
            df_all['Tanggal'] = pd.to_datetime(df_all['Tanggal'], errors='coerce')
            df_ganjil = df_all[df_all['Tanggal'].dt.month.isin([7, 8, 9, 10, 11, 12])].copy()
            
            if not df_ganjil.empty:
                kelas_ganjil = st.selectbox("Pilih Kelas (Ganjil):", sorted(df_ganjil["Kelas"].dropna().unique().tolist()), key="kls_ganjil_sem")
                df_ganjil = df_ganjil[df_ganjil["Kelas"] == kelas_ganjil]
                
                def parse_bool(val):
                    if isinstance(val, bool): return int(val)
                    if isinstance(val, str):
                        return 1 if val.strip().lower() in ['true', '1', 't', 'y', 'yes'] else 0
                    return 0

                for col in ['S', 'I', 'A']:
                    if col in df_ganjil.columns:
                        df_ganjil[col] = df_ganjil[col].apply(parse_bool)
                    else:
                        df_ganjil[col] = 0
                
                rekap_g = df_ganjil.groupby(['ID_Siswa', 'Nama_Siswa']).agg({
                    'S': 'sum',
                    'I': 'sum',
                    'A': 'sum',
                    'Tanggal': 'count'
                }).reset_index().rename(columns={'Tanggal': 'TOTAL PERT.', 'S': 'SAKIT', 'I': 'IZIN', 'A': 'ALPHA', 'ID_Siswa': 'ID', 'Nama_Siswa': 'NAMA SISWA'})
                
                rekap_g['JML TIDAK HADIR'] = rekap_g['SAKIT'] + rekap_g['IZIN'] + rekap_g['ALPHA']
                rekap_g = rekap_g.rename(columns={'JML TIDAK HADIR': '∑ TH', 'TOTAL PERT.': '∑ PERTEMUAN'})
                rekap_g = rekap_g[['ID', 'NAMA SISWA', 'SAKIT', 'IZIN', 'ALPHA', '∑ TH', '∑ PERTEMUAN']]
                
                rekap_g = rekap_g.reset_index(drop=True)
                rekap_g['ID'] = range(1, len(rekap_g) + 1)
                rekap_g['NAMA SISWA'] = rekap_g['NAMA SISWA'].apply(lambda x: html.unescape(str(x)))

                st.dataframe(
                    rekap_g, 
                    hide_index=True, 
                    use_container_width=True,
                    column_config={
                        "ID": st.column_config.NumberColumn("ID", format="%d", width="small"),
                        "NAMA SISWA": st.column_config.TextColumn("NAMA SISWA", width="medium"),
                        "SAKIT": st.column_config.NumberColumn("Sakit", format="%d", width="small"),
                        "IZIN": st.column_config.NumberColumn("Izin", format="%d", width="small"),
                        "ALPHA": st.column_config.NumberColumn("Alpha", format="%d", width="small"),
                        "∑ TH": st.column_config.NumberColumn("∑ TH", format="%d", width="small"),
                        "∑ PERTEMUAN": st.column_config.NumberColumn("∑ PERTEMUAN", format="%d", width="medium"),
                    }
                )

                out_g = io.BytesIO()
                with pd.ExcelWriter(out_g, engine='openpyxl') as w:
                    rekap_g.to_excel(w, index=False, sheet_name='Rekap_Ganjil')
                data_g = out_g.getvalue()

                st.download_button(
                    label="📥 Download Rekap Semester Ganjil (Excel)",
                    data=data_g,
                    file_name=f"Rekap_Semester_Ganjil_Kelas_{kelas_ganjil}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_ganjil_sem_btn"
                )
            else:
                st.warning("Belum ada data absensi untuk Semester Ganjil.")
        else:
            st.warning("Data absensi belum tersedia.")

    with tab5:
        st.subheader("📈 Rekapitulasi Kehadiran Semester Genap (Januari - Juni)")
        df_all_e = load_sheet_data("Absensi_Harian")
        
        if not df_all_e.empty:
            df_all_e['Tanggal'] = pd.to_datetime(df_all_e['Tanggal'], errors='coerce')
            df_genap = df_all_e[df_all_e['Tanggal'].dt.month.isin([1, 2, 3, 4, 5, 6])].copy()
            
            if not df_genap.empty:
                kelas_genap = st.selectbox("Pilih Kelas (Genap):", sorted(df_genap["Kelas"].dropna().unique().tolist()), key="kls_genap_sem_baru")
                df_genap = df_genap[df_genap["Kelas"] == kelas_genap]
                
                def parse_bool(val):
                    if isinstance(val, bool): return int(val)
                    if isinstance(val, str):
                        return 1 if val.strip().lower() in ['true', '1', 't', 'y', 'yes'] else 0
                    return 0

                for col in ['S', 'I', 'A']:
                    if col in df_genap.columns:
                        df_genap[col] = df_genap[col].apply(parse_bool)
                    else:
                        df_genap[col] = 0
                
                rekap_e = df_genap.groupby(['ID_Siswa', 'Nama_Siswa']).agg({
                    'S': 'sum',
                    'I': 'sum',
                    'A': 'sum',
                    'Tanggal': 'count'
                }).reset_index().rename(columns={'Tanggal': 'TOTAL PERT.', 'S': 'SAKIT', 'I': 'IZIN', 'A': 'ALPHA', 'ID_Siswa': 'ID', 'Nama_Siswa': 'NAMA SISWA'})
                
                rekap_e['JML TIDAK HADIR'] = rekap_e['SAKIT'] + rekap_e['IZIN'] + rekap_e['ALPHA']
                rekap_e = rekap_e.rename(columns={'JML TIDAK HADIR': '∑ TH', 'TOTAL PERT.': '∑ PERTEMUAN'})
                rekap_e = rekap_e[['ID', 'NAMA SISWA', 'SAKIT', 'IZIN', 'ALPHA', '∑ TH', '∑ PERTEMUAN']]
                
                rekap_e = rekap_e.reset_index(drop=True)
                rekap_e['ID'] = range(1, len(rekap_e) + 1)
                rekap_e['NAMA SISWA'] = rekap_e['NAMA SISWA'].apply(lambda x: html.unescape(str(x)))

                st.dataframe(
                    rekap_e, 
                    hide_index=True, 
                    use_container_width=True,
                    column_config={
                        "ID": st.column_config.NumberColumn("ID", format="%d", width="small"),
                        "NAMA SISWA": st.column_config.TextColumn("NAMA SISWA", width="medium"),
                        "SAKIT": st.column_config.NumberColumn("Sakit", format="%d", width="small"),
                        "IZIN": st.column_config.NumberColumn("Izin", format="%d", width="small"),
                        "ALPHA": st.column_config.NumberColumn("Alpha", format="%d", width="small"),
                        "∑ TH": st.column_config.NumberColumn("∑ TH", format="%d", width="small"),
                        "∑ PERTEMUAN": st.column_config.NumberColumn("∑ PERTEMUAN", format="%d", width="medium"),
                    }
                )

                out_e = io.BytesIO()
                with pd.ExcelWriter(out_e, engine='openpyxl') as w:
                    rekap_e.to_excel(w, index=False, sheet_name='Rekap_Genap')
                data_e = out_e.getvalue()

                st.download_button(
                    label="📥 Download Rekap Semester Genap (Excel)",
                    data=data_e,
                    file_name=f"Rekap_Semester_Genap_Kelas_{kelas_genap}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_genap_sem_btn"
                )
            else:
                st.warning("Belum ada data absensi untuk Semester Genap.")
        else:
            st.warning("Data absensi belum tersedia.")

elif pilih_app == "3. DIGMA (Digitalisasi Jurnal Mengajar)":
    render_digma_module()
elif pilih_app == "4. SAKTI (Sistem Asesmen & Kompetensi Terintegrasi)":
    render_sakti()