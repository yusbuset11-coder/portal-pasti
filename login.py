import streamlit as st

def render_login():
    # Layout Center untuk Form Login
    _, col_center, _ = st.columns([1, 2.2, 1])
    
    with col_center:
        # Header Portal
        st.markdown("""
            <style>
                .login-header {
                    text-align: center;
                    padding-bottom: 5px;
                }
                .pasti-title {
                    font-size: 3.2rem;
                    font-weight: 900;
                    color: #38bdf8;
                    margin-bottom: 0px;
                    letter-spacing: 2px;
                    line-height: 1.1;
                }
                .pasti-subtitle {
                    font-size: 1.2rem;
                    font-weight: 600;
                    color: #f8fafc;
                    margin-top: 5px;
                    margin-bottom: 10px;
                }
                .pasti-badge {
                    background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%);
                    color: #ffffff;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 0.75rem;
                    font-weight: 700;
                    letter-spacing: 0.8px;
                    display: inline-block;
                    margin-bottom: 15px;
                    box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);
                }
            </style>
            <div class="login-header">
                <div class="pasti-title">PASTI</div>
                <div class="pasti-subtitle">Portal Administrasi Siswa Terintegrasi</div>
                <div class="pasti-badge">PRESENSI SISWA • JURNAL MENGAJAR • ASESMEN PM • MODUL AJAR PM</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Kontainer kartu login yang bersih dan rapi
        with st.container(border=True):
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.9rem; margin-bottom: 20px;'>Silakan masukkan Email dan Token Akses terdaftar di Database Pusat.</p>", unsafe_allow_html=True)
            
            # Form Login Interaktif
            with st.form("form_login_professional"):
                email_input = st.text_input("📧 Email Terdaftar", placeholder="nama.guru@sekolah.id")
                token_input = st.text_input("🔑 Token Akses", type="password", placeholder="Masukkan token rahasia anda")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_btn = st.form_submit_button("🚀 Masuk ke Portal PASTI", use_container_width=True)
                
                if submit_btn:
                    if not email_input or not token_input:
                        st.warning("⚠️ Email dan Token Akses wajib diisi!")
                    else:
                        st.session_state["logged_in"] = True
                        st.session_state["user_email"] = email_input
                        st.success("Login Berhasil! Memuat portal...")
                        st.rerun()