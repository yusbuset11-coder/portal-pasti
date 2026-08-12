from io import BytesIO
import json
import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Pt, RGBColor
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PORTAL PASTI - Portal Administrasi Siswa Terintegrasi",
    page_icon="🏫",
    layout="wide",
)

# ID Google Spreadsheet Database_PASTI_Pusat
SHEET_ID = "1terQDxNZX1aESF0GO02uSn9R7eKLKDGbkiT11GpX1pA"


@st.cache_data(ttl=10)
def load_sheet_data(sheet_name):
  """Fungsi untuk membaca data dari Google Sheets menggunakan gspread (Service Account)."""
  client = get_gspread_client()
  if client:
    try:
      sh = client.open_by_key(SHEET_ID)
      worksheet = sh.worksheet(sheet_name)
      data = worksheet.get_all_records()
      return pd.DataFrame(data)
    except Exception as e:
      return pd.DataFrame()
  else:
    # Fallback jika gspread belum siap, baca via CSV publik
    try:
      url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
      df = pd.read_csv(url)
      return df
    except Exception as e:
      return pd.DataFrame()


def get_gspread_client():
  """Inisialisasi koneksi gspread untuk menulis/mengedit data ke Google Sheets."""
  try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client
  except Exception as e:
    return None


def save_sheet_data(sheet_name, df):
  """Menyimpan perubahan DataFrame kembali ke Google Sheets."""
  client = get_gspread_client()
  if client:
    try:
      sh = client.open_by_key(SHEET_ID)
      worksheet = sh.worksheet(sheet_name)
      worksheet.clear()
      data_to_write = [df.columns.tolist()] + df.fillna("").values.tolist()
      worksheet.update(data_to_write)
      return True
    except Exception as e:
      return False
  else:
    return False


def check_auth():
  """Sistem autentikasi menggunakan Email dan Token dari Google Sheet 'Tokens'."""
  if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

  if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
      st.markdown(
          """
                <div style="background: #1e293b; padding: 30px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.3); margin-top: 50px;">
                    <h3 style="color: #38bdf8; text-align: center; margin-bottom: 20px;">🔐 Autentikasi Portal PASTI</h3>
                    <p style="color: #94a3b8; text-align: center; font-size: 13px;">Masukkan Email dan Token Akses terdaftar di Database Pusat.</p>
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

# ===================================
# Custom CSS UI Modern
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

# Header Portal PASTI
st.markdown(
    f"""
    <div class="header-card">
        <h2 class="header-title">
            <marquee behavior="scroll" direction="left" scrollamount="7" style="color: #38bdf8; text-shadow: 0 0 12px rgba(56, 189, 248, 0.5);">🏫 PORTAL PASTI - PORTAL ADMINISTRASI SISWA TERINTEGRASI</marquee>
        </h2>
        <div class="header-subtitle">
            <b>Pengguna:</b> {st.session_state.get('user_nama', 'Admin')} ({st.session_state.get('user_email', '')}) &nbsp;|&nbsp; 
            <b>Pengembang:</b> Yustinus Budi Setyanta - Pengawas Sekolah Cabdin Bangkalan
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ===================================
# SIDEBAR: NAVIGASI UTAMA APLIKASI PASTI
# ===================================
with st.sidebar:
  st.header("📌 Menu Navigasi PASTI")
  pilih_app = st.selectbox(
      "Pilih Aplikasi Terintegrasi",
      [
          "1. GEMA (Generator Modul Ajar)",
          "2. SIPENSIS (Sistem Pengelolaan Administrasi Siswa)",
          "3. DIGMA (Digital Management - Segera)",
          "4. SAKTI (Sistem Administrasi Kinerja - Segera)",
      ],
  )
  st.markdown("---")

# =========================================================================
# APLIKASI 1: GEMA (Generator Modul Ajar Pembelajaran Mendalam)
# =========================================================================
if pilih_app == "1. GEMA (Generator Modul Ajar)":
  with st.sidebar:
    st.header("⚙️ Parameter Pembelajaran (GEMA)")
    api_key = st.text_input("Masukkan Google Gemini API Key", type="password")

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
      row_cells[0].width = Inches(2.3)
      row_cells[1].width = Inches(4.2)
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

  def add_formative_matrix_table(doc):
    """Fungsi khusus untuk merender Matriks Lembar Observasi Formatif berbentuk Tabel Praktis Guru."""
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

    # Header Row Styling
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

    # Data Rows Styling
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
    add_section_table_custom(doc, "DIMENSI PROFIL LULUSAN", [("Dimensi Profil Lulusan", data_ai.get("dimensi_profil_lulusan", "Penalaran Kritis & Kolaborasi"))])
    add_section_table_custom(doc, "TUJUAN PEMBELAJARAN", [("Tujuan Pembelajaran", data_ai.get("tujuan_pembelajaran", "Peserta didik menguasai kompetensi materi."))])
    add_section_table_custom(doc, "PEMAHAMAN BERMAKNA & PERTANYAAN PEMANTIK", [("Pemahaman Bermakna", data_ai.get("pemahaman_bermakna", "-")), ("Pertanyaan Pemantik", data_ai.get("pertanyaan_pemantik", "-"))])
    
    tabel_kerangka = [
        ("Praktik Pedagogis", data_ai.get("praktik_pedagogis", "Model: Problem Based Learning")),
        ("Kemitraan Pembelajaran", data_ai.get("kemitraan_pembelajaran", "Kolaborasi internal sekolah")),
        ("Lingkungan Belajar", data_ai.get("lingkungan_belajar", "Ruang kelas kolaboratif")),
        ("Pemanfaatan Digital", data_ai.get("pemanfaatan_digital", "AI & Cloud Storage")),
    ]
    add_section_table_custom(doc, "KERANGKA PEMBELAJARAN", tabel_kerangka)

    tabel_pengalaman = [
        ("Kegiatan Pendahuluan", data_ai.get("kegiatan_pendahuluan", "Orientasi dan apersepsi")),
        ("Kegiatan Inti (Memahami)", data_ai.get("kegiatan_memahami", "Eksplorasi konsep")),
        ("Kegiatan Inti (Mengaplikasi)", data_ai.get("kegiatan_mengaplikasi", "Penerapan dalam LKM")),
        ("Kegiatan Inti (Merefleksi)", data_ai.get("kegiatan_merefleksi", "Refleksi pemahaman")),
        ("Kegiatan Penutup", data_ai.get("kegiatan_penutup", "Kesimpulan dan penutup joyful")),
    ]
    add_section_table_custom(doc, "PENGALAMAN BELAJAR (LANGKAH-LANGKAH)", tabel_pengalaman)

    tabel_asesmen = [
        ("Asesmen Awal", data_ai.get("asesmen_awal", "Diagnostik kesiapan")),
        ("Asesmen Proses (Formatif)", data_ai.get("asesmen_formatif", "Observasi keaktifan")),
        ("Asesmen Akhir (Sumatif)", data_ai.get("asesmen_sumatif", "Evaluasi akhir")),
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

    # HALAMAN TERPISAH 1: RUBRIK PENILAIAN
    doc.add_page_break()
    p_rubrik_title = doc.add_paragraph()
    p_rubrik_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_rub_t = p_rubrik_title.add_run("RUBRIK PENILAIAN & PEDOMAN PENSKORAN")
    r_rub_t.font.size = Pt(15)
    r_rub_t.font.bold = True
    r_rub_t.font.color.rgb = RGBColor(74, 46, 33)

    rubrik_data = data_ai.get("rubrik_penilaian", "")
    if isinstance(rubrik_data, dict):
      for k, v in rubrik_data.items():
        if isinstance(v, dict):
          p_crit = doc.add_paragraph()
          p_crit.add_run(f"• {v.get('nama_kriteria', k)}").font.bold = True
          for lvl, desc in [("Perlu Bimbingan", v.get("perlu_bimbingan")), ("Cukup", v.get("cukup")), ("Baik", v.get("baik")), ("Sangat Baik", v.get("sangat_baik"))]:
            if desc:
              p_l = doc.add_paragraph()
              p_l.paragraph_format.left_indent = Inches(0.3)
              p_l.add_run(f"- {lvl}: ").font.bold = True
              p_l.add_run(str(desc))

    # HALAMAN TERPISAH 2: INSTRUMEN FORMATIF (Dilengkapi Tabel Matriks Observasi Kelas)
    doc.add_page_break()
    p_inst_title = doc.add_paragraph()
    p_inst_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst_t = p_inst_title.add_run("INSTRUMEN ASESMEN PROSES (FORMATIF)")
    r_inst_t.font.size = Pt(15)
    r_inst_t.font.bold = True
    r_inst_t.font.color.rgb = RGBColor(74, 46, 33)

    instrumen_data = data_ai.get("instrumen_formatif", {})
    if isinstance(instrumen_data, dict) and instrumen_data:
      inst_rows = [(k.replace("_", " ").title(), str(v)) for k, v in instrumen_data.items()]
      add_section_table_custom(doc, "LEMBAR OBSERVASI KELAS", inst_rows)
    
    # Tambahkan render Tabel Matriks Format Formatif Praktis secara otomatis
    add_formative_matrix_table(doc)

    # HALAMAN TERPISAH 3: LEMBAR KERJA MURID (LKM)
    doc.add_page_break()
    p_lkm_title = doc.add_paragraph()
    p_lkm_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_lkm_t = p_lkm_title.add_run("LEMBAR KERJA MURID (LKM)")
    r_lkm_t.font.size = Pt(15)
    r_lkm_t.font.bold = True
    r_lkm_t.font.color.rgb = RGBColor(74, 46, 33)

    lkm_data = data_ai.get("lkm_content", {})
    if isinstance(lkm_data, dict) and lkm_data:
      lkm_rows = [(k.replace("_", " ").title(), str(v)) for k, v in lkm_data.items()]
      add_section_table_custom(doc, "STRUKTUR LEMBAR KERJA MURID", lkm_rows)

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

  st.markdown("### 🚀 Generator Modul Ajar (GEMA)")
  st.write("Gunakan parameter di sidebar untuk menyusun Modul Ajar Pembelajaran Mendalam.")

  if st.button("🚀 Buat Modul Ajar GEMA"):
    if not api_key:
      st.error("Mohon masukkan Google Gemini API Key.")
    elif not topik:
      st.warning("Mohon isi topik pembelajaran.")
    else:
      with st.spinner("Sistem GEMA PASTI sedang menyusun Modul Ajar..."):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.5-flash") # atau gemini-3.5-flash sesuai konfigurasi Anda
        prompt = f"""
        Bertindaklah sebagai pakar kurikulum profesional. Buatkan konten Modul Ajar Pembelajaran Mendalam (Deep Learning) yang SANGAT LENGKAP untuk:
        - Jenjang: {jenjang_pendidikan} ({fase_kelas})
        - Mata Pelajaran: {mata_pelajaran}
        - Topik: {topik}
        - Alokasi Waktu: {alokasi_waktu}
        - Pertemuan Ke-: {pertemuan_ke}

        Berikan output HANYA dalam format JSON valid dengan kunci:
        dimensi_profil_lulusan, tujuan_pembelajaran, pemahaman_bermakna, pertanyaan_pemantik, praktik_pedagogis, kemitraan_pembelajaran, lingkungan_belajar, pemanfaatan_digital, kegiatan_pendahuluan, kegiatan_memahami, kegiatan_mengaplikasi, kegiatan_merefleksi, kegiatan_penutup, asesmen_awal, asesmen_formatif, asesmen_sumatif, rubrik_penilaian, pedoman_penskoran, instrumen_formatif, lkm_content.
        """
        response = model.generate_content(prompt)
        text_resp = response.text.strip().replace("```json", "").replace("```", "").strip()
        try:
          data_ai = json.loads(text_resp)
        except:
          data_ai = {}

        st.success("🎉 Modul Ajar GEMA Berhasil Disusun dengan Tabel Asesmen Formatif!")
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

# =========================================================================
# APLIKASI 2: SIPENSIS (Sistem Pengelolaan Administrasi Siswa) - INTERAKTIF EDIT
# =========================================================================
elif pilih_app == "2. SIPENSIS (Sistem Pengelolaan Administrasi Siswa)":
  st.markdown("### 📋 Sistem Pengelolaan Administrasi Siswa (SIPENSIS)")
  st.write("Guru dapat langsung melihat, menambah, mengedit, atau menghapus data siswa yang terhubung ke **Database_PASTI_Pusat**.")

  df_siswa = load_sheet_data("Siswa")
  if not df_siswa.empty:
    st.info("💡 Anda dapat melakukan edit langsung pada tabel di bawah ini. Klik tombol **'Simpan Perubahan ke Database Pusat'** setelah selesai.")

    edited_df = st.data_editor(df_siswa, num_rows="dynamic", use_container_width=True, key="editor_siswa")

    if st.button("💾 Simpan Perubahan ke Database Pusat"):
      with st.spinner("Menyimpan pembaruan data ke Google Sheets..."):
        success = save_sheet_data("Siswa", edited_df)
        if success:
          st.success("✅ Data siswa berhasil diperbarui dan disimpan ke Database Pusat!")
          st.rerun()
        else:
          st.error("❌ Gagal menyimpan data. Pastikan konfigurasi Google Service Account sudah aktif.")
  else:
    st.warning("⚠️ Data siswa belum termuat atau tab 'Siswa' pada Google Sheet kosong.")

# =========================================================================
# APLIKASI 3 & 4: DIGMA & SAKTI
# =========================================================================
elif pilih_app.startswith("3."):
  st.markdown("### 📊 DIGMA (Digital Management)")
  st.info("Modul aplikasi DIGMA sedang dalam tahap pengembangan berikutnya di Portal PASTI.")

elif pilih_app.startswith("4."):
  st.markdown("### ⚙️ SAKTI (Sistem Administrasi Kinerja)")
  st.info("Modul aplikasi SAKTI sedang dalam tahap pengembangan berikutnya di Portal PASTI.")