import streamlit as st

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="PASTI - Portal Administrasi Siswa Terintegrasi",
    page_icon="📚",
    layout="wide",
)

# ==========================================
# HALAMAN UTAMA / BERANDA (PORTAL DASHBOARD)
# ==========================================
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

# Ganti URL di bawah ini dengan link Streamlit asli milik masing-masing aplikasi Anda
URL_SIPENSIS = (
    "https://sipensis-nzzezgbxb7qpzxmo2qs9jk.streamlit.app/"  # Contoh link
)
URL_DIGMA = "https://ru27usdatjtkptpha9it3v.streamlit.app/"
URL_SAKTI = "https://kbnmpyijmfge9acfaaynhk.streamlit.app/"
URL_GEMA = "https://generator-modul-ajar-ej7k6d9oggjr6436vsfncn.streamlit.app/"

with col1:
  st.markdown(
      """
        <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; background: white; height: 160px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px;">
            <div>
                <h3 style="color: #2563eb; margin-bottom: 8px; font-size: 18px;">SIPENSIS</h3>
                <p style="font-size: 12px; color: #64748b; margin: 0;">Sistem Informasi Presensi Siswa.</p>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )
  st.link_button(
      "Buka SIPENSIS", URL_SIPENSIS, use_container_width=True, type="primary"
  )

with col2:
  st.markdown(
      """
        <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; background: white; height: 160px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px;">
            <div>
                <h3 style="color: #16a34a; margin-bottom: 8px; font-size: 18px;">DIGMA</h3>
                <p style="font-size: 12px; color: #64748b; margin: 0;">Digitalisasi Jurnal Mengajar Guru.</p>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )
  st.link_button(
      "Buka DIGMA", URL_DIGMA, use_container_width=True, type="primary"
  )

with col3:
  st.markdown(
      """
        <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; background: white; height: 160px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px;">
            <div>
                <h3 style="color: #ca8a04; margin-bottom: 8px; font-size: 18px;">SAKTI</h3>
                <p style="font-size: 12px; color: #64748b; margin: 0;">Sistem Asesmen & Kompetensi Terintegrasi.</p>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )
  st.link_button(
      "Buka SAKTI", URL_SAKTI, use_container_width=True, type="primary"
  )

with col4:
  st.markdown(
      """
        <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; background: white; height: 160px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px;">
            <div>
                <h3 style="color: #dc2626; margin-bottom: 8px; font-size: 18px;">GEMA</h3>
                <p style="font-size: 12px; color: #64748b; margin: 0;">Generator Modul Ajar Pembelajaran Mendalam.</p>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )
  st.link_button("Buka GEMA", URL_GEMA, use_container_width=True, type="primary")

st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #64748b; font-size: 13px;'>© 2026 PASTI"
    " - Yustinus Budi Setyanta, S.Pd., M.Pd. - PS Cabdin Bangkalan</p>",
    unsafe_allow_html=True,
)
