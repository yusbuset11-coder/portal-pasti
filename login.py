"""
Modul: Login PASTI (Otentikasi Berbasis Supabase)
Pengembang: Yustinus Budi Setyanta - Pengawas Sekolah Cabdin Bangkalan
"""

import streamlit as st
import pandas as pd
from supabase import create_client

def get_supabase_client():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def render_login_pasti():
    st.markdown(
        """
        <style>
        .login-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 35px;
            border-radius: 16px;
            border: 1px solid #334155;
            box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.4);
            max-width: 480px;
            margin: 40px auto;
        }
        .login-title {
            color: #f8fafc;
            font-size: 22px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 8px;
        }
        .login-subtitle {
            color: #94a3b8;
            font-size: 13px;
            text-align: center;
            margin-bottom: 25px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div class="login-card">
                <div class="login-title">🏫 PORTAL PASTI</div>
                <div class="login-subtitle">Portal Administrasi Siswa Terintegrasi<br>Silakan masukkan kredensial resmi Anda</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("form_login_pasti"):
            email_input = st.text_input("📧 Email Terdaftar", placeholder="contoh: email@sekolah.id")
            token_input = st.text_input("🔑 Token Unik Akses", type="password", placeholder="Masukkan token rahasia")
            
            submit_login = st.form_submit_button("🔓 Masuk ke Aplikasi", use_container_width=True, type="primary")

            if submit_login:
                if not email_input or not token_input:
                    st.warning("⚠️ Email dan Token wajib diisi dengan lengkap!")
                else:
                    with st.spinner("Memeriksa otorisasi ke Database Supabase..."):
                        try:
                            supabase = get_supabase_client()
                            response = supabase.table("tokens").select("*").eq("email", email_input.strip().lower()).execute()
                            data_user = response.data

                            if data_user:
                                user_record = data_user[0]
                                if str(user_record.get("token")) == token_input.strip():
                                    st.session_state["logged_in"] = True
                                    st.session_state["user_email"] = user_record["email"]
                                    st.session_state["user_nama"] = user_record.get("nama_user", "Guru")
                                    st.session_state["user_sekolah"] = user_record.get("sekolah", "")
                                    st.success("✅ Verifikasi Berhasil! Memuat aplikasi...")
                                    st.rerun()
                                else:
                                    st.error("❌ Akses Ditolak: Token yang Anda masukkan salah.")
                            else:
                                st.error("❌ Akses Ditolak: Email tidak terdaftar di database.")
                        except Exception as e:
                            st.error(f"❌ Gagal terhubung ke database Supabase: {e}")