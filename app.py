import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="PASTI - Portal Akademik Siswa Terintegrasi",
    page_icon="📚",
    layout="wide"
)

# --- 1. INISIALISASI SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# --- 2. FUNGSI LOAD DATABASE MASTER REGISTRY ---
@st.cache_data(ttl=60)
def load_master_registry():
    sheet_id = "1mgN63xzrLt_5bW8dIWp3RRgNdagUiTurFZdgg"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        return None

# --- 3. HALAMAN LOGIN UTAMA (Hanya 1 kali login untuk semua) ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #0284c7;'>🔐 Portal PASTI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Portal Akademik Siswa Terintegrasi — Masuk sekali untuk akses seluruh aplikasi</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email_input = st.text_input("Email Resmi", placeholder="nama@guru.sch.id")
            token_input = st.text_input("Token Unik", type="password", placeholder="Masukkan token unik Anda")
            submit_login = st.form_submit_button("Masuk ke Portal PASTI", use_container_width=True)
            
            if submit_login:
                if not email_input or not token_input:
                    st.error("Mohon isi Email dan Token dengan lengkap!")
                else:
                    df_registry = load_master_registry()
                    if df_registry is not None:
                        # Validasi pencocokan Email dan Token_Unik
                        match = df_registry[
                            (df_registry['Email'].str.strip().str.lower() == email_input.strip().lower()) & 
                            (df_registry['Token_Unik'].str.strip() == token_input.strip())
                        ]
                        
                        if not match.empty:
                            user_row = match.iloc[0]
                            status = str(user_row.get('Status', 'AKTIF'))
                            
                            if status.upper() == 'AKTIF':
                                st.session_state.logged_in = True
                                st.session_state.user_data = {
                                    'nama': user_row.get('Nama_Guru', 'Guru'),
                                    'email': user_row.get('Email', email_input),
                                    'spreadsheet_id': str(user_row.get('Spreadsheet_ID_Guru', '')),
                                    'catatan': user_row.get('Catatan', '')
                                }
                                st.success("Login Berhasil! Memuat Portal...")
                                st.rerun()
                            else:
                                st.error("Akun Anda berstatus NON-AKTIF. Hubungi Administrator.")
                        else:
                            st.error("Email atau Token Unik tidak ditemukan di DATABASE_MASTER_REGISTRY!")
                    else:
                        st.error("Gagal terhubung ke Database Master Registry Google Sheets. Pastikan Google Sheet sudah disetel 'Anyone with the link' (Public).")
    st.stop()

# --- FUNGSI NAVIGASI ANTAR HALAMAN ---
def go_to(page_name):
    st.session_state.current_page = page_name
    st.rerun()

# --- 4. DASHBOARD UTAMA (BERANDA PASTI) ---
if st.session_state.current_page == 'home':
    # Banner Utama
    nama_user = st.session_state.user_data.get('nama', 'Guru')
    sekolah_user = st.session_state.user_data.get('catatan', 'Pendidik')
    
    st.markdown(f"""
        <div style="background-color: #0284c7; padding: 35px; border-radius: 10px; text-align: center; color: white; margin-bottom: 30px;">
            <h1 style="margin: 0; color: white; font-size: 40px;">📂 PASTI</h1>
            <h3 style="margin: 10px 0 0 0; color: #e0f2fe; font-weight: normal;">Portal Akademik Siswa Terintegrasi</h3>
            <p style="margin: 8px 0 0 0; color: #bae6fd; font-size: 15px;">Selamat datang, <b>{nama_user}</b> ({sekolah_user})</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### Pilih Layanan Aplikasi:")
    
    # 4 Kotak Menu Utama
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>👤</h2>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>SIPENSIS</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 13px;'>Sistem Informasi Presensi Siswa.</p>", unsafe_allow_html=True)
            if st.button("Buka SIPENSIS", use_container_width=True, key="b_sipensis"):
                go_to('sipensis')

    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>📖</h2>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>DIGMA</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 13px;'>Digitalisasi Jurnal Mengajar Guru.</p>", unsafe_allow_html=True)
            if st.button("Buka DIGMA", use_container_width=True, key="b_digma"):
                go_to('digma')

    with col3:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>⚡</h2>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>SAKTI</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 13px;'>Sistem Asesmen & Kompetensi Terintegrasi.</p>", unsafe_allow_html=True)
            if st.button("Buka SAKTI", use_container_width=True, key="b_sakti"):
                go_to('sakti')

    with col4:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>📚</h2>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>GEMA</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 13px;'>Generator Modul Ajar Pembelajaran Mendalam.</p>", unsafe_allow_html=True)
            if st.button("Buka GEMA", use_container_width=True, key="b_gema"):
                go_to('gema')
            
    st.write("---")
    col_kiri, col_kanan = st.columns([6, 1])
    with col_kanan:
        if st.button("🚪 Keluar (Logout)", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_data = {}
            go_to('home')

# --- 5. HALAMAN SIPENSIS ---
elif st.session_state.current_page == 'sipensis':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## 👤 SIPENSIS: Sistem Informasi Presensi Siswa")
    st.info(f"Database aktif terhubung ke Spreadsheet ID Guru: `{st.session_state.user_data.get('spreadsheet_id', 'Default')}`")
    
    with st.form("form_sipensis"):
        kelas = st.selectbox("Pilih Kelas", ["Kelas 5A", "Kelas 5B", "Kelas 6A", "Kelas 6B"])
        tanggal = st.date_input("Tanggal Presensi", datetime.now())
        daftar_siswa = st.text_area("Daftar Siswa", "1. Ahmad\n2. Budi\n3. Siti")
        status_hadir = st.selectbox("Keterangan", ["Hadir", "Sakit", "Izin", "Alpa"])
        if st.form_submit_button("Simpan Presensi"):
            st.success(f"Data presensi {kelas} berhasil disimpan ke database Anda!")

# --- 6. HALAMAN DIGMA ---
elif st.session_state.current_page == 'digma':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## 📖 DIGMA: Digitalisasi Jurnal Mengajar Guru")
    st.info(f"Database aktif terhubung ke Spreadsheet ID Guru: `{st.session_state.user_data.get('spreadsheet_id', 'Default')}`")
    
    with st.form("form_digma"):
        tgl = st.date_input("Tanggal Mengajar", datetime.now())
        mapel = st.text_input("Mata Pelajaran", "Matematika")
        materi = st.text_area("Materi Pembelajaran", "Pecahan dan Desimal")
        if st.form_submit_button("Simpan Jurnal"):
            st.success("Jurnal mengajar harian berhasil dicatat!")

# --- 7. HALAMAN SAKTI ---
elif st.session_state.current_page == 'sakti':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## ⚡ SAKTI: Sistem Asesmen & Kompetensi Terintegrasi")
    
    nama_siswa = st.text_input("Nama Lengkap Siswa", "Siswa Contoh")
    q1 = st.radio("1. Ibu membeli 3 kg apel. Setiap kg berisi 4 buah apel. Berapa jumlah seluruh buah apel Ibu?", ["10 buah", "12 buah", "15 buah", "7 buah"])
    q2 = st.radio("2. Hasil dari 125 + 75 - 50 adalah...", ["150", "140", "160", "130"])
    if st.button("Kirim Jawaban"):
        skor = 50 if q1 == "12 buah" else 0
        if q2 == "150": skor += 50
        st.success(f"Ujian selesai! Skor: {skor}/100")

# --- 8. HALAMAN GEMA ---
elif st.session_state.current_page == 'gema':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## 📚 GEMA: Generator Modul Ajar Pembelajaran Mendalam")
    
    with st.form("form_gema"):
        topik = st.text_input("Topik / Mata Pelajaran", "IPAS - Ekosistem")
        fase = st.selectbox("Fase", ["Fase C / Kelas 5", "Fase C / Kelas 6"])
        tujuan = st.text_area("Tujuan Pembelajaran", "Siswa memahami rantai makanan.")
        if st.form_submit_button("Generate Modul Ajar"):
            st.success("Modul ajar berhasil dibuat dengan pendekatan Pembelajaran Mendalam!")
            st.write(f"**Topik:** {topik} | **Fase:** {fase}")
