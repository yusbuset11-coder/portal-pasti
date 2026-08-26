from datetime import datetime
from io import BytesIO
import docx
from docx.shared import Inches, Pt, RGBColor
import google.generativeai as genai
import streamlit as st

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="PASTI - Portal Administrasi Siswa Terintegrasi",
    page_icon="📚",
    layout="wide",
)

# --- NAVIGASI SESSION STATE ---
if "page" not in st.session_state:
  st.session_state.page = "Home"


def navigate_to(page_name):
  st.session_state.page = page_name
  st.rerun()


# --- KONEKSI GEMINI AI ---
@st.cache_resource
def init_gemini():
  try:
    if "GEMINI_API_KEY" in st.secrets:
      genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
      return True
  except Exception:
    return False
  return False


init_gemini()

# ==========================================
# HALAMAN UTAMA (DASHBOARD PORTAL PASTI)
# ==========================================
if st.session_state.page == "Home":
  st.markdown(
      """
        <div style="background: linear-gradient(135deg, #0284c7, #0369a1); padding: 35px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h1 style="margin: 0; font-size: 38px; font-weight: bold; letter-spacing: 1px;">PASTI</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Portal Administrasi Siswa Terintegrasi</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  col1, col2, col3, col4 = st.columns(4)

  with col1:
    st.markdown(
        """
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; background: white; height: 180px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div>
                    <h3 style="color: #2563eb; margin-bottom: 8px; font-size: 18px;">SIPENSIS</h3>
                    <p style="font-size: 12px; color: #64748b; margin: 0;">Sistem Informasi Presensi Siswa.</p>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "Buka SIPENSIS", use_container_width=True, key="btn_sipensis"
    ):
      navigate_to("SIPENSIS")

  with col2:
    st.markdown(
        """
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; background: white; height: 180px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div>
                    <h3 style="color: #16a34a; margin-bottom: 8px; font-size: 18px;">DIGMA</h3>
                    <p style="font-size: 12px; color: #64748b; margin: 0;">Digitalisasi Jurnal Mengajar Guru.</p>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Buka DIGMA", use_container_width=True, key="btn_digma"):
      navigate_to("DIGMA")

  with col3:
    st.markdown(
        """
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; background: white; height: 180px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div>
                    <h3 style="color: #ca8a04; margin-bottom: 8px; font-size: 18px;">SAKTI</h3>
                    <p style="font-size: 12px; color: #64748b; margin: 0;">Sistem Asesmen & Kompetensi Terintegrasi.</p>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Buka SAKTI", use_container_width=True, key="btn_sakti"):
      navigate_to("SAKTI")

  with col4:
    st.markdown(
        """
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; background: white; height: 180px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div>
                    <h3 style="color: #dc2626; margin-bottom: 8px; font-size: 18px;">GEMA</h3>
                    <p style="font-size: 12px; color: #64748b; margin: 0;">Generator Modul Ajar Pembelajaran Mendalam.</p>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Buka GEMA", use_container_width=True, key="btn_gema"):
      navigate_to("GEMA")

  st.markdown("<br><hr><br>", unsafe_allow_html=True)
  st.markdown(
      "<p style='text-align: center; color: #64748b; font-size: 13px;'>© 2026"
      " PASTI - Yustinus Budi Setyanta, S.Pd., M.Pd. - PS Cabdin Bangkalan</p>",
      unsafe_allow_html=True,
  )

# ==========================================
# HALAMAN MODUL KETIKA DIPILIH
# ==========================================
else:
  if st.button("⬅️ Kembali ke Beranda Portal PASTI", type="secondary"):
    navigate_to("Home")

  st.markdown("---")

  if st.session_state.page == "SIPENSIS":
    st.title("👥 SIPENSIS: Sistem Informasi Presensi Siswa")
    st.info("Modul presensi siswa sedang disiapkan.")

  elif st.session_state.page == "DIGMA":
    st.title("📖 DIGMA: Digitalisasi Jurnal Mengajar Guru")
    st.info("Modul jurnal mengajar guru sedang disiapkan.")

  elif st.session_state.page == "SAKTI":
    st.title("⚡ SAKTI: Sistem Asesmen & Kompetensi Terintegrasi")
    st.info("Modul asesmen dan rekap nilai sedang disiapkan.")

  elif st.session_state.page == "GEMA":
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0284c7, #0369a1); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
            <h2 style="margin: 0; font-size: 24px;">📚 GEMA: Generator Modul Ajar Pembelajaran Mendalam</h2>
            <p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">Penyusunan perangkat ajar Kurikulum Merdeka berbasis Deep Learning</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
      mapel = st.text_input("Mata Pelajaran", placeholder="Contoh: Bahasa Indonesia")
      jenjang = st.selectbox(
          "Jenjang", ["-- Pilih Jenjang --", "SD", "SMP", "SMA", "SMK"]
      )

    if jenjang == "SD":
      fase_options = [
          "Fase A (Kelas 1-2)",
          "Fase B (Kelas 3-4)",
          "Fase C (Kelas 5-6)",
      ]
      kelas_options = [
          "Kelas 1",
          "Kelas 2",
          "Kelas 3",
          "Kelas 4",
          "Kelas 5",
          "Kelas 6",
      ]
    elif jenjang == "SMP":
      fase_options = ["Fase D (Kelas 7-9)"]
      kelas_options = ["Kelas 7", "Kelas 8", "Kelas 9"]
    elif jenjang in ["SMA", "SMK"]:
      fase_options = ["Fase E (Kelas 10)", "Fase F (Kelas 11-12)"]
      kelas_options = ["Kelas 10", "Kelas 11", "Kelas 12"]
    else:
      fase_options = ["-- Pilih Jenjang Dulu --"]
      kelas_options = ["-- Pilih Jenjang Dulu --"]

    with col2:
      materi = st.text_input(
          "Materi / Topik Pembelajaran",
          placeholder="Contoh: Menyimak Teks Laporan Observasi",
      )
      fase = st.selectbox("Fase", fase_options)

    col3, col4 = st.columns(2)
    with col3:
      kelas = st.selectbox("Kelas", kelas_options)
    with col4:
      alokasi = st.text_input("Alokasi Waktu", value="2 JP (2 x 45 Menit)")

    if st.button(
        "🚀 Generate Modul Ajar dengan Gemini AI", use_container_width=True
    ):
      if jenjang == "-- Pilih Jenjang --" or not mapel or not materi:
        st.warning("Mohon lengkapi Mata Pelajaran, Materi, dan pilih Jenjang!")
      else:
        with st.spinner(
            "⏳ Sedang menyusun Modul Ajar Pembelajaran Mendalam..."
        ):
          try:
            prompt = f"""Bertindaklah sebagai pakar kurikulum dan guru profesional. Buatkan dokumen Modul Ajar Kurikulum Merdeka yang lengkap dan mendalam menggunakan pendekatan Pembelajaran Mendalam (Deep Learning) untuk:
                    - Mata Pelajaran: {mapel}
                    - Materi/Topik: {materi}
                    - Jenjang/Fase/Kelas: {jenjang} / {fase} / {kelas}
                    - Alokasi Waktu: {alokasi}

                    Sajikan secara terstruktur mencakup:
                    1. Informasi Umum (Identitas, Kompetensi Awal, Profil Pelajar Pancasila, Sarana Prasarana, Target Peserta Didik, Model Pembelajaran)
                    2. Komponen Inti (Tujuan Pembelajaran, Pemahaman Bermakna, Pertanyaan Pemantik, Persiapan Pembelajaran)
                    3. Kegiatan Pembelajaran (Pendahuluan, Inti dengan sintaks pembelajaran mendalam, Penutup)
                    4. Asesmen (Formatif & Sumatif lengkap dengan instrumennya)
                    5. Lampiran (LKPD, Bahan Bacaan, Glosarium, Daftar Pustaka)"""

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            st.session_state.gema_result = response.text
            st.session_state.gema_mapel = mapel
            st.session_state.gema_materi = materi
            st.session_state.gema_kelas = kelas
            st.session_state.gema_jenjang = jenjang
            st.session_state.gema_fase = fase
            st.session_state.gema_alokasi = alokasi

            st.success("✅ Modul Ajar Berhasil Disusun!")
          except Exception as e:
            st.error(f"Gagal menghasilkan modul: {e}")

    if "gema_result" in st.session_state and st.session_state.gema_result:
      st.markdown("### 📋 Hasil Modul Ajar:")
      st.markdown(st.session_state.gema_result)


      def generate_word_doc(
          mp, mt, kl, jnj, fs, alk, text_content
      ):
        doc = docx.Document()
        p_title = doc.add_paragraph()
        r_title = p_title.add_run("MODUL AJAR KURIKULUM MERDEKA")
        r_title.bold = True
        r_title.font.name = "Cambria"
        r_title.font.size = Pt(14)
        r_title.font.color.rgb = RGBColor(0, 51, 102)

        for line in text_content.split("\n"):
          if line.strip():
            p = doc.add_paragraph()
            run = p.add_run(line.strip())
            run.font.name = "Cambria"
            run.font.size = Pt(10.5)

        bio = BytesIO()
        doc.save(bio)
        bio.seek(0)
        return bio


      docx_file = generate_word_doc(
          st.session_state.gema_mapel,
          st.session_state.gema_materi,
          st.session_state.gema_kelas,
          st.session_state.gema_jenjang,
          st.session_state.gema_fase,
          st.session_state.gema_alokasi,
          st.session_state.gema_result,
      )

      st.download_button(
          label="📥 Download Modul Ajar Format Word (.docx)",
          data=docx_file,
          file_name=(
              f"Modul_Ajar_{st.session_state.gema_mapel}_{st.session_state.gema_materi}.docx".replace(
                  " ", "_"
              )
          ),
          mime=(
              "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          ),
          use_container_width=True,
      )
