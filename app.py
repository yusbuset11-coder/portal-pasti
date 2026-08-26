import streamlit as st

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="PASTI - Portal Akademik Siswa Terintegrasi",
    page_icon="📚",
    layout="wide",
)

# --- CSS CUSTOM UNTUK TAMPILAN RINGKAS & ELEGAN ---
st.markdown(
    """
    <style>
    /* Mengurangi jarak atas agar tidak terlalu ke bawah */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Header Utama yang Lebih Kompak */
    .main-header {
        background: linear-gradient(135deg, #0284c7, #38bdf8);
        padding: 25px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Desain Kartu Menu */
    .card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px 15px;
        text-align: center;
        height: 205px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 10px;
    }
    
    .card-icon {
        font-size: 32px;
        margin-bottom: 2px;
    }
    
    .card-title {
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 3px;
    }
    
    .card-desc {
        font-size: 11px;
        color: #64748b;
        margin: 0;
    }
    
    /* Tombol Navigasi Dalam Portal */
    .stButton button {
        width: 100%;
        border-radius: 20px;
        font-weight: 500;
        font-size: 13px;
        padding: 4px 0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SESSION STATE UNTUK LOGIN & NAVIGASI ---
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if "page" not in st.session_state:
  st.session_state.page = "Home"


def navigate_to(page_name):
  st.session_state.page = page_name
  st.rerun()


# ==========================================
# HALAMAN LOGIN (SEKALI DI AWAL)
# ==========================================
if not st.session_state.logged_in:
  col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
  with col_l2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: white; padding: 30px; border-radius: 15px; border: 1.5px solid #e2e8f0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center;">
            <h2 style="color: #0284c7; margin-bottom: 5px;">🔐 Portal PASTI</h2>
            <p style="font-size: 13px; color: #64748b;">Silakan masukkan Email dan Token Unik Anda</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    email_input = st.text_input("Email Resmi", placeholder="nama@guru.sch.id")
    token_input = st.text_input(
        "Token Unik", type="password", placeholder="Masukkan token unik Anda"
    )

    if st.button("Masuk ke Portal", type="primary", use_container_width=True):
      if email_input and token_input:  # Validasi bebas atau sesuaikan token Anda
        st.session_state.logged_in = True
        st.session_state.email = email_input
        st.success("Login Berhasil! Memuat Portal...")
        st.rerun()
      else:
        st.warning("Mohon isi Email dan Token Unik terlebih dahulu!")

# ==========================================
# SETELAH LOGIN (DASHBOARD UTAMA)
# ==========================================
else:
  if st.session_state.page == "Home":
    st.markdown(
        """
        <div class="main-header">
            <div style="font-size: 32px; margin-bottom: 2px;">🗂️</div>
            <h1 style="margin: 0; font-size: 32px; font-weight: bold; letter-spacing: 1px;">PASTI</h1>
            <p style="margin: 5px 0 0 0; font-size: 15px; opacity: 0.95;">Portal Akademik Siswa Terintegrasi</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
      st.markdown(
          """
            <div class="card">
                <div>
                    <div class="card-icon">👤</div>
                    <div class="card-title" style="color: #2563eb;">SIPENSIS</div>
                    <div class="card-desc">Sistem Informasi Presensi Siswa.</div>
                </div>
            </div>
        """,
          unsafe_allow_html=True,
      )
      if st.button(
          "Buka SIPENSIS", key="btn_sipensis", type="secondary", use_container_width=True
      ):
        navigate_to("SIPENSIS")

    with col2:
      st.markdown(
          """
            <div class="card">
                <div>
                    <div class="card-icon">📖</div>
                    <div class="card-title" style="color: #16a34a;">DIGMA</div>
                    <div class="card-desc">Digitalisasi Jurnal Mengajar Guru.</div>
                </div>
            </div>
        """,
          unsafe_allow_html=True,
      )
      if st.button(
          "Buka DIGMA", key="btn_digma", type="secondary", use_container_width=True
      ):
        navigate_to("DIGMA")

    with col3:
      st.markdown(
          """
            <div class="card">
                <div>
                    <div class="card-icon">📝</div>
                    <div class="card-title" style="color: #ca8a04;">SAKTI</div>
                    <div class="card-desc">Sistem Asesmen & Kompetensi Terintegrasi.</div>
                </div>
            </div>
        """,
          unsafe_allow_html=True,
      )
      if st.button(
          "Buka SAKTI", key="btn_sakti", type="secondary", use_container_width=True
      ):
        navigate_to("SAKTI")

    with col4:
      st.markdown(
          """
            <div class="card">
                <div>
                    <div class="card-icon">🤖</div>
                    <div class="card-title" style="color: #dc2626;">GEMA</div>
                    <div class="card-desc">Generator Modul Ajar Pembelajaran Mendalam.</div>
                </div>
            </div>
        """,
          unsafe_allow_html=True,
      )
      if st.button(
          "Buka GEMA", key="btn_gema", type="secondary", use_container_width=True
      ):
        navigate_to("GEMA")

    # Tombol Logout di bawah
    st.markdown("<br>", unsafe_allow_html=True)
    col_out1, col_out2, col_out3 = st.columns([2, 1, 2])
    with col_out2:
      if st.button("🚪 Keluar / Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #64748b; font-size: 12px;'>©"
        " 2026 PASTI - Yustinus Budi Setyanta, S.Pd., M.Pd. - PS Cabdin"
        " Bangkalan</p>",
        unsafe_allow_html=True,
    )

  # ==========================================
  # SUB HALAMAN MODUL
  # ==========================================
  else:
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
      navigate_to("Home")

    st.markdown("---")

    if st.session_state.page == "SIPENSIS":
      st.title("👥 SIPENSIS: Sistem Informasi Presensi Siswa")
      st.info("Modul presensi siswa aktif di dalam portal terintegrasi.")
    elif st.session_state.page == "DIGMA":
      st.title("📖 DIGMA: Digitalisasi Jurnal Mengajar Guru")
      st.info("Modul jurnal mengajar guru aktif di dalam portal terintegrasi.")
    elif st.session_state.page == "SAKTI":
      st.title("⚡ SAKTI: Sistem Asesmen & Kompetensi Terintegrasi")
      st.info("Modul asesmen dan rekap nilai aktif di dalam portal terintegrasi.")
    elif st.session_state.page == "GEMA":
      st.title("📚 GEMA: Generator Modul Ajar Pembelajaran Mendalam")
      st.info("Modul generator perangkat ajar aktif di dalam portal terintegrasi.")
