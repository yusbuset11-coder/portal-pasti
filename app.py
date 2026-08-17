"""
Aplikasi Utama: PASTI (Portal Administrasi Siswa Terintegrasi)
Pengembang: Yustinus Budi Setyanta - Pengawas Sekolah Cabdin Bangkalan
"""

import streamlit as st

# Impor modul-modul termasuk login
from login import render_login_pasti
from gema import render_gema
from sipensis import render_sipensis
from digma import render_digma_module
from sakti import render_sakti

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="PASTI - Portal Administrasi Siswa Terintegrasi",
    page_icon="🏫",
    layout="wide",
)

# === PENGECEKAN LOGIN & TOKEN DATABASE ===
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    render_login_pasti()
    st.stop()

# --- CSS KUSTOM GLOBAL ---
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 25%, #1e293b 0%, #090d16 100%) !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
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
        font-size: 16px;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.3px;
    }
    .header-subtitle {
        font-size: 12px;
        margin-top: 6px;
        margin-bottom: 0;
        font-weight: 500;
        color: #94a3b8;
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Informasi Pengguna yang Berhasil Login
st.markdown(
    f"""
    <div class="header-card">
        <h2 class="header-title">
            🏫 PASTI - PORTAL ADMINISTRASI SISWA TERINTEGRASI
        </h2>
        <div class="header-subtitle">
            <b>Pengguna:</b> {st.session_state.get('user_nama', 'Admin')} ({st.session_state.get('user_sekolah', '')}) &nbsp;|&nbsp; 
            <b>Pengembang:</b> Yustinus Budi Setyanta - Pengawas Sekolah Cabdin Bangkalan[cite: 5]
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR NAVIGASI UTAMA ---
with st.sidebar:
    st.header("📌 Menu Navigasi PASTI")
    pilih_app = st.selectbox(
        "Pilih Aplikasi Terintegrasi",
        [
            "1. GEMA (Generator Modul Ajar)",
            "2. SIPENSIS (Sistem Informasi Presensi Siswa)",
            "3. DIGMA (Digitalisasi Jurnal Mengajar)",
            "4. SAKTI (Sistem Asesmen & Kompetensi Terintegrasi)",
        ],
    )
    
    st.markdown("---")
    st.subheader("🔑 Konfigurasi AI")
    api_key_input = st.text_input("Masukkan Google Gemini API Key", type="password", key="input_gemini_key")
    if api_key_input:
        st.session_state["gemini_api_key"] = api_key_input

    st.markdown("---")
    if st.button("🚪 Keluar (Logout)", type="secondary", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()

st.markdown("---")

# --- PEMANGGILAN MODUL BERDASARKAN PILIHAN MENU ---
if pilih_app == "1. GEMA (Generator Modul Ajar)":
    render_gema()
elif pilih_app == "2. SIPENSIS (Sistem Informasi Presensi Siswa)":
    render_sipensis()
elif pilih_app == "3. DIGMA (Digitalisasi Jurnal Mengajar)":
    render_digma_module()
elif pilih_app == "4. SAKTI (Sistem Asesmen & Kompetensi Terintegrasi)":
    render_sakti()