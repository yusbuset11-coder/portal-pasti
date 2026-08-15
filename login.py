import streamlit as st

def render_login():
    # Inject Custom CSS untuk Tampilan Web Profesional
    st.markdown("""
        <style>
            .login-card {
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                padding: 45px 35px;
                border-radius: 20px;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(56, 189, 248, 0.2);
                text-align: center;
                margin-top: 20px;
                margin-bottom: 20px;
            }
            .pasti-title {
                font-size: 3.5rem;
                font-weight: 900;
                color: #38bdf8;
                margin-bottom: 0px;
                letter-spacing: 2px;
                line-height: 1;
            }
            .pasti-subtitle {
                font-size: 1.3rem;
                font-weight: 600;
                color: #f8fafc;
                margin-top: 6px;
                margin-bottom: 18px;
            }
            .pasti-features-badge {
                display: inline-block;
                background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%);
                color: #ffffff;
                padding: 6px 18px;
                border-radius: 30px;
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0.8px;
                margin-bottom: 22px;
                box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
            .pasti-instruction {
                color: #94a3b8;
                font-size: 0.95rem;
                margin-bottom: 0px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Layout Center untuk Kartu Login
    _, col_center, _ = st.columns([1, 2.2, 1])
    
    with col_center:
        st.markdown("""
            <div class="login-card">
                <div class="pasti-title">PASTI</div>
                <div class="pasti-subtitle">Portal Administrasi Siswa Terintegrasi</div>
                <div class="pasti-features-badge">PRESENSI SISWA - JURNAL MENGAJAR - ASESMEN PM - MODUL AJAR PM</div>
                <div class="pasti-instruction">Masukkan Email dan Token Akses terdaftar di Database Pusat.</div>
            </div>
        """, unsafe_allow_html=True)

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