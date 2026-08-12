from datetime import datetime
from io import BytesIO
import json
import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Pt, RGBColor
import google.generativeai as genai
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PASTI - Portal Administrasi Siswa Terintegrasi",
    page_icon="🏛️",
    layout="wide",
)

# ===================================
# KONFIGURASI DATA DINAMIS JENJANG
# ===================================
JENJANG_CONFIG = {
    "SD / MI": {
        "default_mapel": "Tematik / Kelas",
        "jp_guidance": "Panduan: 1 JP = 35 Menit",
        "fase_options": [
            "Fase A / Kelas 1 SD",
            "Fase A / Kelas 2 SD",
            "Fase B / Kelas 3 SD",
            "Fase B / Kelas 4 SD",
            "Fase C / Kelas 5 SD",
            "Fase C / Kelas 6 SD",
        ],
    },
    "SMP / MTs": {
        "default_mapel": "Matematika / IPA / IPS",
        "jp_guidance": "Panduan: 1 JP = 40 Menit",
        "fase_options": [
            "Fase D / Kelas 7 SMP",
            "Fase D / Kelas 8 SMP",
            "Fase D / Kelas 9 SMP",
        ],
    },
    "SMA / MA": {
        "default_mapel": "Bahasa Indonesia / Matematika",
        "jp_guidance": "Panduan: 1 JP = 45 Menit",
        "fase_options": [
            "Fase E / Kelas X SMA",
            "Fase F / Kelas XI SMA",
            "Fase F / Kelas XII SMA",
        ],
    },
    "SMK / MAK": {
        "default_mapel": (
            "Dasar-dasar Teknik Otomotif / Produk Kreatif dan Kewirausahaan"
        ),
        "jp_guidance": "Panduan: 1 JP = 45 Menit",
        "fase_options": [
            "Fase E / Kelas X SMK (Program Dasar Keahlian)",
            "Fase F / Kelas XI SMK (Konsentrasi Keahlian)",
            "Fase F / Kelas XII SMK (Konsentrasi Keahlian)",
        ],
    },
}

# ===================================
# AUTENTIKASI BERBASIS GOOGLE SHEETS
# ===================================
def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user_sekolah"] = ""
        st.session_state["user_nama"] = ""

    if not st.session_state["authenticated"]:
        st.markdown(
            """
            <div style="max-width: 450px; margin: 40px auto; padding: 30px; background: #1e293b; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                <h2 style="color: #f8fafc; text-align: center; margin-bottom: 10px; font-size: 20px;">🔐 Autentikasi PASTI</h2>
                <p style="color: #94a3b8; text-align: center; font-size: 13px; margin-bottom: 20px;">Masukkan Email dan Token Akses Anda dari Pengawas.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            input_email = st.text_input("📧 Email Pengguna")
            input_token = st.text_input("🔑 Token Akses", type="password")

            if st.button("Masuk Portal PASTI"):
                try:
                    sheet_id = "1terQDxNZX1aESF0GO02uSn9R7eKLKDGbkiT11GpX1pA"
                    url_tokens = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Tokens"
                    df_tokens = pd.read_csv(url_tokens)
                    
                    df_tokens = df_tokens.dropna(subset=['Email'])
                    
                    df_tokens['Email'] = df_tokens['Email'].astype(str).str.strip().str.lower()
                    df_tokens['Token'] = df_tokens['Token'].astype(str).str.strip()
                    
                    match = df_tokens[(df_tokens['Email'] == input_email.strip().lower()) & (df_tokens['Token'] == input_token.strip())]
                    
                    if not match.empty:
                        st.session_state["authenticated"] = True
                        st.session_state["user_nama"] = match.iloc[0]['Nama']
                        st.session_state["user_sekolah"] = match.iloc[0]['Sekolah']
                        st.rerun()
                    else:
                        st.error("❌ Email atau Token salah.")
                except Exception as e:
                    st.error(f"Error Database: {e}")
        return False
    return True

if not check_auth():
    st.stop()

# ===================================
# CSS & TAMPILAN UTAMA
# ===================================
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

# ===================================
# NAVIGASI UTAMA DI SIDEBAR
# ===================================
with st.sidebar:
    st.write(f"👤 **{st.session_state['user_nama']}**")
    st.write(f"🏫 *{st.session_state['user_sekolah']}*")
    if st.button("🚪 Keluar (Logout)"):
        st.session_state["authenticated"] = False
        st.rerun()

    st.markdown("---")
    st.header("🧭 Navigasi PASTI")
    pilih_modul = st.selectbox(
        "Pilih Modul Aplikasi",
        [
            "📚 GEMA (Generator Modul Ajar)",
            "📋 SIPENSIS (Sistem Presensi Siswa)",
        ],
    )

    st.markdown("---")

    if pilih_modul.startswith("📚"):
        st.header("⚙️ Parameter Pembelajaran")
        api_key = st.text_input(
            "Masukkan Google Gemini API Key", type="password", key="gema_api"
        )

        jenjang_pendidikan = st.selectbox(
            "Pilih Jenjang Pendidikan", list(JENJANG_CONFIG.keys())
        )

        config = JENJANG_CONFIG[jenjang_pendidikan]

        mata_pelajaran = st.text_input(
            "Mata Pelajaran / Program Kejuruan", config["default_mapel"]
        )
        fase_kelas = st.selectbox("Fase / Kelas", config["fase_options"])

        topik = st.text_input(
            "Topik / Materi Pokok / Elemen",
            (
                "Contoh: Pemeliharaan Sistem Rem Kendaraan Ringan"
                if jenjang_pendidikan == "SMK / MAK"
                else "Contoh: Menyimak Teks Laporan Observasi Secara Kritis"
            ),
        )

        st.caption(config["jp_guidance"])
        alokasi_waktu = st.text_input("Alokasi Waktu", "2 JP (2 x 45 Menit)")
        pertemuan_ke = st.text_input("Pertemuan Ke-", "1 (Pertemuan Pertama)")

        st.markdown("---")
        st.header("🏫 Identitas Satuan Pendidikan")
        nama_sekolah = st.text_input("Nama Sekolah", st.session_state['user_sekolah'])
        semester = st.selectbox("Semester", ["Ganjil", "Genap"])
        tahun_pelajaran = st.text_input("Tahun Pelajaran", "2026/2027")

        st.markdown("---")
        st.header("✍️ Identitas Pengesahan Dokumen")
        nama_kota = st.text_input("Nama Kota", "Bangkalan")
        tanggal_pembuatan = st.text_input(
            "Tanggal / Bulan / Tahun", "11 Agustus 2026"
        )
        nama_penulis = st.text_input(
            "Nama Penulis Modul", st.session_state['user_nama']
        )
        nip_penulis = st.text_input("NIP Penulis", "196908302005011003")
    else:
        st.header("⚙️ Pengaturan SIPENSIS")
        tanggal_presensi = st.date_input("Tanggal Presensi", datetime.today())

# TAMPILAN HEADER UTAMA DINAMIS
judul_modul_aktif = (
    "📚 GEMA - GENERATOR MODUL AJAR PEMBELAJARAN MENDALAM"
    if pilih_modul.startswith("📚")
    else "📋 SIPENSIS - SISTEM PRESENSI DAN REKAPITULASI OTOMATIS"
)

st.markdown(
    f"""
    <div class="header-card">
        <h2 class="header-title">
            <marquee behavior="scroll" direction="left" scrollamount="7" style="color: #38bdf8; text-shadow: 0 0 12px rgba(56, 189, 248, 0.5);">🏛️ PASTI - PORTAL ADMINISTRASI SISWA TERINTEGRASI</marquee>
        </h2>
        <div class="header-subtitle">
            <b>Modul Aktif:</b> {judul_modul_aktif} &nbsp;|&nbsp; 
            <em>Pengembang: Yustinus Budi Setyanta - PS Cabdin Bangkalan</em>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ===================================
# FUNGSI GENERATOR DOCX (GEMA)
# ===================================
def set_cell_background(cell, fill_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def generate_docx(
    data_ai,
    nama_sekolah,
    semester,
    tahun_pelajaran,
    mata_pelajaran,
    fase_kelas,
    topik,
    alokasi_waktu,
    pertemuan_ke,
    nama_penulis,
    nama_kota,
    tanggal_pembuatan,
    nip_penulis,
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

    def add_section_table(title_text, rows_data):
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
                p.paragraph_format.line_spacing = 1.15
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    run.font.size = Pt(10)
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(51, 51, 51)

            val_str = str(val).replace("LKPD", "LKM").replace("Lembar Kegiatan Murid", "Lembar Kerja Murid")
            row_cells[1].text = ""
            lines = val_str.split("\n")
            for line_idx, line in enumerate(lines):
                if line_idx == 0:
                    p_right = row_cells[1].paragraphs[0]
                else:
                    p_right = row_cells[1].add_paragraph()

                p_right.paragraph_format.space_before = Pt(4)
                p_right.paragraph_format.space_after = Pt(4)
                p_right.paragraph_format.line_spacing = 1.15
                p_right.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

                if ":" in line:
                    parts = line.split(":", 1)
                    prefix = parts[0].strip() + ":"
                    content = parts[1].strip()
                    r_prefix = p_right.add_run(prefix + " ")
                    r_prefix.font.size = Pt(10)
                    r_prefix.font.bold = True
                    r_prefix.font.color.rgb = RGBColor(51, 51, 51)
                    r_content = p_right.add_run(content)
                    r_content.font.size = Pt(10)
                    r_content.font.bold = False
                    r_content.font.color.rgb = RGBColor(51, 51, 51)
                else:
                    r_normal = p_right.add_run(line)
                    r_normal.font.size = Pt(10)
                    r_normal.font.bold = False
                    r_normal.font.color.rgb = RGBColor(51, 51, 51)

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

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
    add_section_table("IDENTIFIKASI DAN INFORMASI UMUM", tabel_identifikasi)

    tabel_dpl = [
        (
            "Dimensi Profil Lulusan",
            data_ai.get(
                "dimensi_profil_lulusan",
                "☑ Penalaran Kritis: Peserta didik dilatih menganalisis masalah secara logis.\n☑ Kolaborasi: Bekerja sama dalam kelompok investigasi.\n☑ Kemandirian: Bertanggung jawab atas tugas mandiri.\n☑ Komunikasi: Mempresentasikan hasil kerja.",
            ),
        ),
    ]
    add_section_table("DIMENSI PROFIL LULUSAN", tabel_dpl)

    tabel_tujuan = [
        (
            "Tujuan Pembelajaran",
            data_ai.get("tujuan_pembelajaran", "Peserta didik mampu menguasai kompetensi sesuai materi."),
        ),
    ]
    add_section_table("TUJUAN PEMBELAJARAN", tabel_tujuan)

    tabel_pemahaman = [
        (
            "Pemahaman Bermakna",
            data_ai.get("pemahaman_bermakna", "Manfaat praktis dan esensi pembelajaran bagi kehidupan."),
        ),
        (
            "Pertanyaan Pemantik",
            data_ai.get("pertanyaan_pemantik", "Pertanyaan kritis untuk menstimulasi rasa ingin tahu peserta didik."),
        ),
    ]
    add_section_table("PEMAHAMAN BERMAKNA & PERTANYAAN PEMANTIK", tabel_pemahaman)

    tabel_kerangka = [
        (
            "Praktik Pedagogis",
            data_ai.get(
                "praktik_pedagogis",
                "Model Pembelajaran: Problem Based Learning\nMetode Pembelajaran Pendukung: Diskusi, Tanya Jawab, Analisis Teks",
            ),
        ),
        (
            "Kemitraan Pembelajaran",
            data_ai.get(
                "kemitraan_pembelajaran",
                "Kemitraan Lingkungan Sekolah: Kolaborasi guru mapel produktif.\nKemitraan Lingkungan Luar Sekolah: Pemanfaatan data/narasumber instansi terkait.",
            ),
        ),
        (
            "Lingkungan Belajar",
            data_ai.get(
                "lingkungan_belajar",
                "Ruang Fisik: Kelas fleksibel dan kolaboratif.\nRuang Virtual: Google Drive / LMS Sekolah.\nBudaya Belajar: Kolaboratif, Berpikir Kritis, Keterbukaan.",
            ),
        ),
        (
            "Pemanfaatan Digital",
            data_ai.get(
                "pemanfaatan_digital",
                "Tahap Perencanaan: AI & Cloud Storage.\nTahap Pelaksanaan: QR Code & Audio/Video Digital.\nTahap Asesmen: Google Form / Menti.",
            ),
        ),
    ]
    add_section_table("KERANGKA PEMBELAJARAN", tabel_kerangka)

    tabel_pengalaman = [
        ("Kegiatan Pendahuluan", data_ai.get("kegiatan_pendahuluan", "Orientasi, Apersepsi, Motivasi, dan Asesmen Diagnostik awal.")),
        ("Kegiatan Inti (Memahami)", data_ai.get("kegiatan_memahami", "Eksplorasi konsep dan penyajian masalah autentik.")),
        ("Kegiatan Inti (Mengaplikasi)", data_ai.get("kegiatan_mengaplikasi", "Penyelidikan kolaboratif dan penerapan konsep dalam LKM.")),
        ("Kegiatan Inti (Merefleksi)", data_ai.get("kegiatan_merefleksi", "Presentasi kelompok, umpan balik konstruktif, dan penguatan.")),
        ("Kegiatan Penutup", data_ai.get("kegiatan_penutup", "Refleksi bersama yang menyenangkan (joyful) dan bermakna.")),
    ]
    add_section_table("PENGALAMAN BELAJAR (LANGKAH-LANGKAH)", tabel_pengalaman)

    tabel_asesmen = [
        ("Asesmen Awal", data_ai.get("asesmen_awal", "Cek kesiapan sebelum masuk topik pembelajaran.")),
        ("Asesmen Proses (Formatif)", data_ai.get("asesmen_formatif", "Pemantauan partisipasi, keaktifan, dan pemahaman selama kegiatan.")),
        ("Asesmen Akhir (Sumatif)", data_ai.get("asesmen_sumatif", "Evaluasi hasil berbasis unjuk kerja atau refleksi kedalaman konsep.")),
    ]
    add_section_table("ASESMEN PEMBELAJARAN", tabel_asesmen)

    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.space_before = Pt(14)
    p_sign.paragraph_format.space_after = Pt(4)
    p_sign.add_run(f"{nama_kota}, {tanggal_pembuatan}\nPenyusun,\n\n\n")
    run_name = p_sign.add_run(f"{nama_penulis}")
    run_name.font.bold = True
    p_sign.add_run(f"\nNIP. {nip_penulis}")

    # BAGIAN 2: RUBRIK PENILAIAN
    doc.add_page_break()
    p_rubrik_title = doc.add_paragraph()
    p_rubrik_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rubrik_title.paragraph_format.space_before = Pt(0)
    p_rubrik_title.paragraph_format.space_after = Pt(12)
    r_rub_t = p_rubrik_title.add_run("RUBRIK PENILAIAN & PEDOMAN PENSKORAN")
    r_rub_t.font.name = "Arial"
    r_rub_t.font.size = Pt(15)
    r_rub_t.font.bold = True
    r_rub_t.font.color.rgb = RGBColor(74, 46, 33)

    table_id_rubrik = doc.add_table(rows=3, cols=2)
    table_id_rubrik.style = "Table Grid"
    table_id_rubrik.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_id_rubrik.rows[0].cells[0].text = "Nama Guru / Pengamat:"
    table_id_rubrik.rows[0].cells[1].text = f"{nama_penulis}"
    table_id_rubrik.rows[1].cells[0].text = "Kelas / Fase:"
    table_id_rubrik.rows[1].cells[1].text = f"{fase_kelas}"
    table_id_rubrik.rows[2].cells[0].text = "Mata Pelajaran / Topik:"
    table_id_rubrik.rows[2].cells[1].text = f"{mata_pelajaran} - {topik}"

    for row in table_id_rubrik.rows:
        row.cells[0].width = Inches(2.3)
        row.cells[1].width = Inches(4.2)
        set_cell_background(row.cells[0], "F5EBE0")
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)
                for run in p.runs:
                    run.font.size = Pt(10)
                    run.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    rubrik_data = data_ai.get("rubrik_penilaian", "")
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(6)
    p_sub.paragraph_format.space_after = Pt(4)
    run_sub = p_sub.add_run("A. Rubrik Penilaian Kinerja / Kompetensi")
    run_sub.font.bold = True
    run_sub.font.size = Pt(10)
    run_sub.font.color.rgb = RGBColor(51, 51, 51)

    if isinstance(rubrik_data, dict):
        for k, v in rubrik_data.items():
            if isinstance(v, dict):
                nama = v.get("nama_kriteria", k)
                pb = v.get("perlu_bimbingan", "")
                c = v.get("cukup", "")
                b = v.get("baik", "")
                sb = v.get("sangat_baik", "")
                p_crit = doc.add_paragraph()
                p_crit.paragraph_format.space_before = Pt(4)
                p_crit.paragraph_format.space_after = Pt(2)
                p_crit.paragraph_format.left_indent = Inches(0.2)
                r_nama = p_crit.add_run(f"• {nama}")
                r_nama.font.bold = True
                r_nama.font.size = Pt(10)

                for level_name, level_desc in [
                    ("Perlu Bimbingan", pb),
                    ("Cukup", c),
                    ("Baik", b),
                    ("Sangat Baik", sb),
                ]:
                    if level_desc:
                        p_lvl = doc.add_paragraph()
                        p_lvl.paragraph_format.space_before = Pt(1)
                        p_lvl.paragraph_format.space_after = Pt(2)
                        p_lvl.paragraph_format.left_indent = Inches(0.4)
                        p_lvl.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                        r_l_name = p_lvl.add_run(f"- {level_name}: ")
                        r_l_name.font.bold = True
                        r_l_name.font.size = Pt(9.5)
                        r_l_desc = p_lvl.add_run(f"{str(level_desc).replace('LKPD', 'LKM').replace('Lembar Kegiatan Murid', 'Lembar Kerja Murid')}")
                        r_l_desc.font.bold = False
                        r_l_desc.font.size = Pt(9.5)

    # BAGIAN 3: INSTRUMEN ASESMEN PROSES (FORMATIF)
    doc.add_page_break()
    p_ins_title = doc.add_paragraph()
    p_ins_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ins_title.paragraph_format.space_before = Pt(0)
    p_ins_title.paragraph_format.space_after = Pt(12)
    r_ins_t = p_ins_title.add_run("INSTRUMEN ASESMEN PROSES (FORMATIF)")
    r_ins_t.font.name = "Arial"
    r_ins_t.font.size = Pt(15)
    r_ins_t.font.bold = True
    r_ins_t.font.color.rgb = RGBColor(74, 46, 33)

    tabel_id_instrumen = doc.add_table(rows=3, cols=2)
    tabel_id_instrumen.style = "Table Grid"
    tabel_id_instrumen.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabel_id_instrumen.rows[0].cells[0].text = "Nama Guru / Pengamat:"
    tabel_id_instrumen.rows[0].cells[1].text = f"{nama_penulis}"
    tabel_id_instrumen.rows[1].cells[0].text = "Kelas / Fase:"
    tabel_id_instrumen.rows[1].cells[1].text = f"{fase_kelas}"
    tabel_id_instrumen.rows[2].cells[0].text = "Mata Pelajaran / Topik:"
    tabel_id_instrumen.rows[2].cells[1].text = f"{mata_pelajaran} - {topik}"

    for row in tabel_id_instrumen.rows:
        row.cells[0].width = Inches(2.3)
        row.cells[1].width = Inches(4.2)
        set_cell_background(row.cells[0], "F5EBE0")
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)
                for run in p.runs:
                    run.font.size = Pt(10)
                    run.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    instrumen_data = data_ai.get("instrumen_asesmen_formatif", "Lembar observasi keaktifan dan keterlibatan peserta didik selama proses pembelajaran.")
    p_inst_desc = doc.add_paragraph()
    p_inst_desc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_inst_desc.paragraph_format.space_before = Pt(4)
    p_inst_desc.paragraph_format.space_after = Pt(6)
    r_id_text = p_inst_desc.add_run(str(instrumen_data))
    r_id_text.font.size = Pt(10)

    # BAGIAN 4: LEMBAR KERJA MURID (LKM)
    doc.add_page_break()
    p_lkm_title = doc.add_paragraph()
    p_lkm_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lkm_title.paragraph_format.space_before = Pt(0)
    p_lkm_title.paragraph_format.space_after = Pt(12)
    r_lkm_t = p_lkm_title.add_run("LEMBAR KERJA MURID (LKM)")
    r_lkm_t.font.name = "Arial"
    r_lkm_t.font.size = Pt(15)
    r_lkm_t.font.bold = True
    r_lkm_t.font.color.rgb = RGBColor(74, 46, 33)

    table_id_lkm = doc.add_table(rows=4, cols=2)
    table_id_lkm.style = "Table Grid"
    table_id_lkm.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_id_lkm.rows[0].cells[0].text = "Nama Kelompok / Siswa:"
    table_id_lkm.rows[0].cells[1].text = "..........................................................................."
    table_id_lkm.rows[1].cells[0].text = "Kelas / Fase:"
    table_id_lkm.rows[1].cells[1].text = f"{fase_kelas}"
    table_id_lkm.rows[2].cells[0].text = "Mata Pelajaran:"
    table_id_lkm.rows[2].cells[1].text = f"{mata_pelajaran}"
    table_id_lkm.rows[3].cells[0].text = "Topik / Materi:"
    table_id_lkm.rows[3].cells[1].text = f"{topik}"

    for row in table_id_lkm.rows:
        row.cells[0].width = Inches(2.3)
        row.cells[1].width = Inches(4.2)
        set_cell_background(row.cells[0], "F5EBE0")
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)
                for run in p.runs:
                    run.font.size = Pt(10)
                    run.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    lkm_content = data_ai.get("lembar_kerja_murid", "Panduan kerja, tugas investigasi, dan rubrik pengerjaan tugas mandiri/kelompok.")
    p_lkm_body = doc.add_paragraph()
    p_lkm_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_lkm_body.paragraph_format.space_before = Pt(4)
    p_lkm_body.paragraph_format.space_after = Pt(6)
    r_lkm_body = p_lkm_body.add_run(str(lkm_content).replace("LKPD", "LKM").replace("Lembar Kegiatan Murid", "Lembar Kerja Murid"))
    r_lkm_body.font.size = Pt(10)

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# ===================================
# EKSEKUSI MODUL GEMA
# ===================================
if pilih_modul.startswith("📚"):
    if st.button("🚀 Buat Modul Ajar Pembelajaran Mendalam"):
        if not api_key:
            st.error("Mohon masukkan Google Gemini API Key terlebih dahulu.")
        elif not topik:
            st.warning("Mohon isi topik pembelajaran.")
        else:
            with st.spinner("Yusbuset sedang menyusun Modul Ajar Pembelajaran Mendalam lengkap dengan Instrumen Asesmen dan LKM ..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-3.5-flash")

                prompt = f"""
                Bertindaklah sebagai pakar kurikulum profesional. Buatkan konten Modul Ajar Berbasis Pembelajaran Mendalam (Deep Learning) yang **SANGAT LENGKAP, DETAIL, DAN KOMPREHENSIF** untuk:
                - Jenjang: {jenjang_pendidikan} ({fase_kelas})
                - Mata Pelajaran: {mata_pelajaran}
                - Topik / Materi Pokok: {topik}
                - Alokasi Waktu: {alokasi_waktu}
                - Pertemuan Ke-: {pertemuan_ke}

                Berikan output HANYA dalam format JSON valid yang memuat kunci-kunci berikut:
                {{
                  "dimensi_profil_lulusan": "Hanya tuliskan dimensi profil lulusan yang dipilih saja (gunakan tanda ☑) beserta uraian penerapannya.",
                  "tujuan_pembelajaran": "Uraian tujuan pembelajaran yang spesifik, operasional, dan terukur sesuai materi.",
                  "pemahaman_bermakna": "Uraian pemahaman bermakna yang mendalam terkait materi.",
                  "pertanyaan_pemantik": "2 pertanyaan pemantik yang kontekstual dan menantang daya nalar kritis siswa.",
                  "praktik_pedagogis": "Model Pembelajaran: [Isi model]\\nMetode Pembelajaran Pendukung: [Isi metode dengan penomoran]",
                  "kemitraan_pembelajaran": "Kemitraan Lingkungan Sekolah: [Isi]\\nKemitraan Lingkungan Luar Sekolah: [Isi]",
                  "lingkungan_belajar": "Ruang Fisik: [Isi]\\nRuang Virtual: [Isi]\\nBudaya Belajar: [Isi]",
                  "pemanfaatan_digital": "Tahap Perencanaan: [Isi]\\nTahap Pelaksanaan: [Isi]\\nTahap Asesmen: [Isi]",
                  "kegiatan_pendahuluan": "Langkah rinci kegiatan pendahuluan.",
                  "kegiatan_memahami": "Langkah rinci kegiatan inti pada tahap Memahami.",
                  "kegiatan_mengaplikasi": "Langkah rinci kegiatan inti pada tahap Mengaplikasi menggunakan LKM.",
                  "kegiatan_merefleksi": "Langkah rinci kegiatan inti pada tahap Merefleksi.",
                  "kegiatan_penutup": "Langkah rinci kegiatan penutup.",
                  "asesmen_awal": "Uraian asesmen awal.",
                  "asesmen_formatif": "Uraian asesmen proses/formatif.",
                  "asesmen_sumatif": "Uraian asesmen akhir/sumatif.",
                  "rubrik_penilaian": {{
                    "kriteria_1": {{
                      "nama_kriteria": "Nama kriteria pertama",
                      "perlu_bimbingan": "Deskripsi...",
                      "cukup": "Deskripsi...",
                      "baik": "Deskripsi...",
                      "sangat_baik": "Deskripsi..."
                    }}
                  }},
                  "instrumen_asesmen_formatif": "Uraian rinci instrumen asesmen proses (formatif) berupa panduan observasi, lembar ceklis keterlibatan, atau catatan kemajuan belajar peserta didik.",
                  "lembar_kerja_murid": "Uraian lengkap Lembar Kerja Murid (LKM) yang mencakup petunjuk pengerjaan, instruksi tugas/investigasi kelompok, dan ruang kerja peserta didik."
                }}
                """

                response = model.generate_content(prompt)
                text_resp = response.text.strip()
                if text_resp.startswith("```json"):
                    text_resp = text_resp[7:]
                if text_resp.startswith("```"):
                    text_resp = text_resp[3:]
                if text_resp.endswith("```"):
                    text_resp = text_resp[:-3]
                text_resp = text_resp.strip()

                try:
                    data_ai = json.loads(text_resp)
                except Exception:
                    data_ai = {}

                st.success("🎉 Modul Ajar Beserta Asesmen & LKM Berhasil Disusun!")
                docx_file = generate_docx(
                    data_ai,
                    nama_sekolah,
                    semester,
                    tahun_pelajaran,
                    mata_pelajaran,
                    fase_kelas,
                    topik,
                    alokasi_waktu,
                    pertemuan_ke,
                    nama_penulis,
                    nama_kota,
                    tanggal_pembuatan,
                    nip_penulis,
                )

                st.download_button(
                    label="📥 Unduh Modul Ajar & Kelengkapan Pembelajaran (.docx)",
                    data=docx_file,
                    file_name=f"Modul_Ajar_{topik.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

# ===================================
# EKSEKUSI MODUL SIPENSIS (ISOLASI SEKOLAH)
# ===================================
else:
    st.subheader(f"📋 Sistem Presensi Siswa - {st.session_state['user_sekolah']}")

    try:
        sheet_id = "1terQDxNZX1aESF0GO02uSn9R7eKLKDGbkiT11GpX1pA"
        url_siswa = f"[https://docs.google.com/spreadsheets/d/](https://docs.google.com/spreadsheets/d/){sheet_id}/gviz/tq?tqx=out:csv&sheet=Siswa"
        df_siswa_pusat = pd.read_csv(url_siswa)
        
        df_siswa_pusat = df_siswa_pusat.dropna(subset=['Sekolah'])
        
        sekolah_guru = st.session_state["user_sekolah"]
        df_sekolah_ini = df_siswa_pusat[df_siswa_pusat['Sekolah'].str.strip().str.lower() == sekolah_guru.strip().lower()]
        
        daftar_kelas = df_sekolah_ini['Kelas'].dropna().unique().tolist()
        
        if daftar_kelas:
            kelas_pilihan = st.selectbox("Pilih Kelas", daftar_kelas)
            daftar_nama_siswa = df_sekolah_ini[df_sekolah_ini['Kelas'] == kelas_pilihan]['Nama Siswa'].dropna().tolist()
            
            st.write(f"Menampilkan data siswa untuk kelas **{kelas_pilihan}** ({sekolah_guru})")
            
            if daftar_nama_siswa:
                with st.form("form_presensi_sekolah"):
                    absensi_input = {}
                    
                    col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([3, 1, 1, 1, 1])
                    col_h1.markdown("**Nama Siswa**")
                    col_h2.markdown("**Hadir**")
                    col_h3.markdown("**Sakit**")
                    col_h4.markdown("**Izin**")
                    col_h5.markdown("**Alpha**")

                    for siswa in daftar_nama_siswa:
                        c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
                        c1.text(siswa)
                        status = c2.radio(
                            f"stat_{siswa}",
                            ["H", "S", "I", "A"],
                            horizontal=True,
                            label_visibility="collapsed",
                            key=f"r_{kelas_pilihan}_{siswa}"
                        )
                        absensi_input[siswa] = status
                    
                    submitted = st.form_submit_button("📊 Simpan & Proses Rekapitulasi")
                
                if submitted:
                    h = list(absensi_input.values()).count("H")
                    s = list(absensi_input.values()).count("S")
                    i = list(absensi_input.values()).count("I")
                    a = list(absensi_input.values()).count("A")
                    total = len(daftar_nama_siswa)
                    persentase = ((h + i) / total) * 100 if total > 0 else 0
                    
                    st.success("Data presensi berhasil direkap!")
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.metric("Total Siswa", total)
                    m2.metric("Hadir (H)", h)
                    m3.metric("Sakit (S)", s)
                    m4.metric("Izin (I)", i)
                    m5.metric("Alpha (A)", a)
                    
                    st.info(f"Persentase Kehadiran (Hadir + Izin): **{persentase:.2f}%**")
                    df_rekap = pd.DataFrame(list(absensi_input.items()), columns=["Nama Siswa", "Status Kehadiran"])
                    st.dataframe(df_rekap, use_container_width=True)
            else:
                st.warning(f"⚠️ Belum ada nama siswa yang terdaftar di kelas **{kelas_pilihan}**.")
        else:
            st.warning(f"⚠️ Belum ada data kelas/siswa untuk sekolah **{sekolah_guru}** di Google Sheet tab 'Siswa'.")
            
    except Exception as e:
        st.error(f"Gagal memuat data siswa dari Google Sheets: {e}")