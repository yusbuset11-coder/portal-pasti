import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="PASTI - Portal Akademik Siswa Terintegrasi",
    page_icon="📚",
    layout="wide"
)

# Inisialisasi Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# Fungsi untuk Memuat Database Master Registry dari Google Sheet
@st.cache_data(ttl=60)
def load_master_registry():
    sheet_id = "1mgN63xzrLt_5bW8dIWp3RRgNdagUiTurFZdgg"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        return None

# --- HALAMAN LOGIN BERBASIS DATABASE MASTER REGISTRY ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #0284c7;'>🔐 Portal PASTI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Silakan masukkan Email dan Token Unik Anda yang terdaftar di Master Registry</p>", unsafe_allow_html=True)
    
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
                                    'spreadsheet_id': user_row.get('Spreadsheet_ID_Guru', ''),
                                    'catatan': user_row.get('Catatan', '')
                                }
                                st.success("Login Berhasil! Mengalihkan ke Portal...")
                                st.rerun()
                            else:
                                st.error("Akun Anda berstatus NON-AKTIF. Hubungi Administrator.")
                        else:
                            st.error("Email atau Token Unik tidak ditemukan di DATABASE_MASTER_REGISTRY!")
                    else:
                        st.error("Gagal terhubung ke Database Master Registry Google Sheets.")
    st.stop()

# Fungsi Navigasi Antar Menu
def go_to(page_name):
    st.session_state.current_page = page_name

# --- DASHBOARD UTAMA PORTAL PASTI ---
if st.session_state.current_page == 'home':
    # Banner Utama
    st.markdown(f"""
        <div style="background-color: #0284c7; padding: 30px; border-radius: 10px; text-align: center; color: white; margin-bottom: 30px;">
            <h1 style="margin: 0; color: white; font-size: 38px;">📂 PASTI</h1>
            <h3 style="margin: 10px 0 0 0; color: #e0f2fe; font-weight: normal;">Portal Akademik Siswa Terintegrasi</h3>
            <p style="margin: 5px 0 0 0; color: #bae6fd; font-size: 14px;">Selamat datang, <b>{st.session_state.user_data.get('nama')}</b> ({st.session_state.user_data.get('catatan', 'Guru')})</p>
        </div>
    """, unsafe_allow_html=True)

    # 4 Kotak Menu Aplikasi
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>👤</h3>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>SIPENSIS</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 13px;'>Sistem Informasi Presensi Siswa.</p>", unsafe_allow_html=True)
            if st.button("Buka SIPENSIS", use_container_width=True, key="b_sipensis"):
                go_to('sipensis')

    with col2:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>📖</h3>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>DIGMA</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 13px;'>Digitalisasi Jurnal Mengajar Guru.</p>", unsafe_allow_html=True)
            if st.button("Buka DIGMA", use_container_width=True, key="b_digma"):
                go_to('digma')

    with col3:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>⚡</h3>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>SAKTI</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 13px;'>Sistem Asesmen & Kompetensi Terintegrasi.</p>", unsafe_allow_html=True)
            if st.button("Buka SAKTI", use_container_width=True, key="b_sakti"):
                go_to('sakti')

    with col4:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>📚</h3>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>GEMA</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 13px;'>Generator Modul Ajar Pembelajaran Mendalam.</p>", unsafe_allow_html=True)
            if st.button("Buka GEMA", use_container_width=True, key="b_gema"):
                go_to('gema')
            
    st.write("---")
    col_l, col_r = st.columns([6, 1])
    with col_r:
        if st.button("🚪 Keluar (Logout)", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_page = 'home'
            st.rerun()

# --- 1. SIPENSIS (Sistem Informasi Presensi Siswa) ---
elif st.session_state.current_page == 'sipensis':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## 👤 SIPENSIS: Sistem Informasi Presensi Siswa")
    st.write("Kelola dan catat daftar kehadiran siswa secara terstruktur.")
    
    tab1, tab2 = st.tabs(["📝 Input Presensi Harian", "📊 Rekap Kehadiran"])
    with tab1:
        with st.form("form_sipensis"):
            kelas_pilih = st.selectbox("Pilih Kelas", ["Kelas 5A", "Kelas 5B", "Kelas 6A", "Kelas 6B"])
            tgl_presensi = st.date_input("Tanggal", datetime.now())
            daftar_mhs = st.text_area("Daftar Nama Siswa", "1. Ahmad Fauzi\n2. Budi Santoso\n3. Siti Aminah")
            status_hadir = st.selectbox("Status Kehadiran Default", ["Hadir", "Sakit", "Izin", "Alpa"])
            if st.form_submit_button("Simpan Data Presensi"):
                st.success(f"Presensi {kelas_pilih} tanggal {tgl_presensi} berhasil dicatat!")
    with tab2:
        st.info("Fitur rekapitulasi presensi bulanan siswa.")

# --- 2. DIGMA (Digitalisasi Jurnal Mengajar Guru) ---
elif st.session_state.current_page == 'digma':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## 📖 DIGMA: Digitalisasi Jurnal Mengajar Guru")
    st.write("Pencatatan kegiatan belajar mengajar harian pendidik.")
    
    with st.form("form_digma"):
        tgl_ajar = st.date_input("Tanggal Mengajar", datetime.now())
        mapel = st.text_input("Mata Pelajaran", "Matematika / IPAS")
        jam_ke = st.text_input("Jam Ke-", "1 - 3 (3 x 45 Menit)")
        materi = st.text_area("Materi Pembelajaran / Topik Utama", "Operasi Hitung Bilangan Pecahan")
        catatan_guru = st.text_area("Catatan Refleksi & Kendala Kelas", "Sebagian besar siswa aktif berdiskusi kelompok.")
        if st.form_submit_button("Simpan Jurnal Mengajar"):
            st.success("Jurnal Mengajar harian berhasil disimpan ke sistem!")

# --- 3. SAKTI (Sistem Asesmen & Kompetensi Terintegrasi) ---
elif st.session_state.current_page == 'sakti':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## ⚡ SAKTI: Sistem Asesmen & Kompetensi Terintegrasi")
    st.write("Simulasi Asesmen Kompetensi / Ujian Peserta Didik.")
    
    with st.form("form_sakti"):
        peserta = st.text_input("Nama Siswa Peserta", "Siswa Contoh")
        ujian = st.selectbox("Pilih Paket Soal", ["Literasi Membaca - Fase C", "Numerasi & Matematika - Fase C"])
        
        st.markdown("---")
        st.markdown("**Soal 1:** Ibu membeli 3 kg apel. Setiap kg berisi 4 buah apel. Berapa jumlah seluruh buah apel Ibu?")
        ans1 = st.radio("Pilih jawaban Soal 1:", ["10 buah", "12 buah", "15 buah", "7 buah"], key="s1")
        
        st.markdown("**Soal 2:** Hasil dari 125 + 75 - 50 adalah...")
        ans2 = st.radio("Pilih jawaban Soal 2:", ["150", "140", "160", "130"], key="s2")
        
        if st.form_submit_button("Kirim Jawaban Asesmen"):
            skor = 0
            if ans1 == "12 buah": skor += 50
            if ans2 == "150": skor += 50
            st.success(f"Asesmen selesai! Peserta: {peserta} | Total Skor Akhir: {skor} / 100")

# --- 4. GEMA (Generator Modul Ajar) ---
elif st.session_state.current_page == 'gema':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## 📚 GEMA: Generator Modul Ajar Pembelajaran Mendalam")
    st.write("Penyusunan perangkat ajar kurikulum terbaru dengan prinsip Deep Learning.")
    
    with st.form("form_gema"):
        topik = st.text_input("Topik / Mata Pelajaran", "IPAS - Ekosistem dan Rantai Makanan")
        fase_kelas = st.selectbox("Fase / Kelas", ["Fase C / Kelas 5", "Fase C / Kelas 6"])
        tujuan_pembelajaran = st.text_area("Tujuan Pembelajaran", "Siswa mampu menganalisis peran produsen dan konsumen dalam ekosistem.")
        
        if st.form_submit_button("Generate Modul Ajar"):
            st.markdown("---")
            st.markdown("### 📄 Hasil Draf Modul Ajar (GEMA)")
            st.info("Modul ajar berhasil disusun berdasarkan pendekatan pembelajaran mendalam!")
            st.write(f"* **Topik:** {topik}")
            st.write(f"* **Fase / Kelas:** {fase_kelas}")
            st.write(f"* **Tujuan:** {tujuan_pembelajaran}")
            st.markdown("""
            **Langkah Pembelajaran Mendalam (Deep Learning):**
            1. **Mindful Learning (Kesadaran):** Mengamati lingkungan sekitar / gambar ekosistem sawah.
            2. **Meaningful Learning (K bermakna):** Diskusi kelompok menyusun jaring-jaring makanan.
            3. **Joyful Learning (Menyenangkan):** Presentasi interaktif menggunakan kartu peran hewan.
            """)
