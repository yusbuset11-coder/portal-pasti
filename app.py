import streamlit as st

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="PASTI - Portal Akademik Siswa Terintegrasi",
    page_icon="📚",
    layout="wide",
)

# --- CSS CUSTOM UNTUK MENIRU DESAIN LAMA YANG ELEGAN ---
st.markdown(
    """
    <style>
    /* Gradasi Header Utama */
    .main-header {
        background: linear-gradient(135deg, #0284c7, #38bdf8);
        padding: 40px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Desain Kartu Menu */
    .card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 25px 20px;
        text-align: center;
        height: 225px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 15px;
    }
    
    .card-icon {
        font-size: 36px;
        margin-bottom: 5px;
    }
    
    .card-title {
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 5px;
    }
    
    .card-desc {
        font-size: 12px;
        color: #64748b;
        margin: 0;
    }
    
    /* Tombol Outline Custom */
    .btn-custom {
        display: block;
        width: 100%;
        padding: 8px 0;
        text-align: center;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
        text-decoration: none;
        transition: all 0.2s;
        background: white;
    }
    
    .btn-sipensis { border: 1.5px solid #2563eb; color: #2563eb; }
    .btn-sipensis:hover { background: #2563eb; color: white; }

    .btn-digma { border: 1.5px solid #16a34a; color: #16a34a; }
    .btn-digma:hover { background: #16a34a; color: white; }

    .btn-sakti { border: 1.5px solid #ca8a04; color: #ca8a04; }
    .btn-sakti:hover { background: #ca8a04; color: white; }

    .btn-gema { border: 1.5px solid #dc2626; color: #dc2626; }
    .btn-gema:hover { background: #dc2626; color: white; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- HEADER UTAMA ---
st.markdown(
    """
    <div class="main-header">
        <div style="font-size: 40px; margin-bottom: 5px;">🗂️</div>
        <h1 style="margin: 0; font-size: 36px; font-weight: bold; letter-spacing: 1px;">PASTI</h1>
        <p style="margin: 8px 0 0 0; font-size: 16px; opacity: 0.95;">Portal Akademik Siswa Terintegrasi</p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- LINK APLIKASI MASING-MASING ---
URL_SIPENSIS = "https://sipensis-nzzezgbxb7qpzxmo2qs9jk.streamlit.app/"
URL_DIGMA = "https://ru27usdatjtkptpha9it3v.streamlit.app/"
URL_SAKTI = "https://kbnmpyijmfge9acfaaynhk.streamlit.app/"
URL_GEMA = (
    "https://generator-modul-ajar-ej7k6d9oggjr6436vsfncn.streamlit.app/"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
  st.markdown(
      f"""
        <div class="card">
            <div>
                <div class="card-icon">👤</div>
                <div class="card-title" style="color: #2563eb;">SIPENSIS</div>
                <div class="card-desc">Sistem Informasi Presensi Siswa</div>
            </div>
            <a href="{URL_SIPENSIS}" target="_blank" class="btn-custom btn-sipensis">Buka SIPENSIS</a>
        </div>
    """,
      unsafe_allow_html=True,
  )

with col2:
  st.markdown(
      f"""
        <div class="card">
            <div>
                <div class="card-icon">📖</div>
                <div class="card-title" style="color: #16a34a;">DIGMA</div>
                <div class="card-desc">Digitalisasi Jurnal Mengajar Guru.</div>
            </div>
            <a href="{URL_DIGMA}" target="_blank" class="btn-custom btn-digma">Buka DIGMA</a>
        </div>
    """,
      unsafe_allow_html=True,
  )

with col3:
  st.markdown(
      f"""
        <div class="card">
            <div>
                <div class="card-icon">📝</div>
                <div class="card-title" style="color: #ca8a04;">SAKTI</div>
                <div class="card-desc">Sistem Asesmen & Kompetensi Terintegrasi.</div>
            </div>
            <a href="{URL_SAKTI}" target="_blank" class="btn-custom btn-sakti">Buka SAKTI</a>
        </div>
    """,
      unsafe_allow_html=True,
  )

with col4:
  st.markdown(
      f"""
        <div class="card">
            <div>
                <div class="card-icon">🤖</div>
                <div class="card-title" style="color: #dc2626;">GEMA</div>
                <div class="card-desc">Generator Modul Ajar Pembelajaran Mendalam.</div>
            </div>
            <a href="{URL_GEMA}" target="_blank" class="btn-custom btn-gema">Buka GEMA</a>
        </div>
    """,
      unsafe_allow_html=True,
  )

# --- FOOTER ---
st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #64748b; font-size: 13px;'>© 2026"
    " PASTI - Yustinus Budi Setyanta, S.Pd., M.Pd. - PS Cabdin Bangkalan</p>",
    unsafe_allow_html=True,
)
