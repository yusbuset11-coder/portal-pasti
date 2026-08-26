import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="PASTI - Portal Akademik Siswa Terintegrasi",
    page_icon="📚",
    layout="wide"
)

# Inisialisasi Session State untuk Login dan Navigasi
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# --- HALAMAN LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 Portal PASTI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Silakan masukkan Email dan Token Unik Anda</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email Resmi", placeholder="nama@guru.sch.id")
            token = st.text_input("Token Unik", type="password", placeholder="Masukkan token unik Anda")
            submit = st.form_submit_button("Masuk ke Portal", use_container_width=True)
            
            if submit:
                if email and token:
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.rerun()
                else:
                    st.error("Mohon isi Email dan Token dengan benar!")
    st.stop()

# --- FUNGSI NAVIGASI ---
def go_to(page_name):
    st.session_state.current_page = page_name

# --- DASHBOARD UTAMA ---
if st.session_state.current_page == 'home':
    st.markdown("<h1 style='text-align: center; color: #0284c7;'>📂 PASTI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #64748b;'>Portal Akademik Siswa Terintegrasi</h3>", unsafe_allow_html=True)
    st.write("")
    st.write("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("### 👤 SIPENSIS")
        st.write("Sistem Informasi Presensi Siswa.")
        if st.button("Buka SIPENSIS", use_container_width=True):
            go_to('sipensis')

    with col2:
        st.markdown("### 📖 DIGMA")
        st.write("Digitalisasi Jurnal Mengajar Guru.")
        if st.button("Buka DIGMA", use_container_width=True):
            go_to('digma')

    with col3:
        st.markdown("### ⚡ SAKTI")
        st.write("Sistem Asesmen & Kompetensi Terintegrasi.")
        if st.button("Buka SAKTI", use_container_width=True):
            go_to('sakti')

    with col4:
        st.markdown("### 📚 GEMA")
        st.write("Generator Modul Ajar Pembelajaran Mendalam.")
        if st.button("Buka GEMA", use_container_width=True):
            go_to('gema')
            
    st.write("---")
    if st.button("🚪 Keluar (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

# --- 1. SIPENSIS (Presensi Siswa) ---
elif st.session_state.current_page == 'sipensis':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## 👤 SIPENSIS: Sistem Informasi Presensi Siswa")
    st.write("Gunakan halaman ini untuk mencatat dan merekap kehadiran siswa.")
    
    with st.form("form_presensi"):
        kelas = st.selectbox("Pilih Kelas", ["Kelas 5A", "Kelas 5B", "Kelas 6A", "Kelas 6B"])
        tanggal = st.date_input("Tanggal Presensi", datetime.now())
        nama_siswa = st.text_area("Daftar Siswa (Pisahkan dengan baris baru)", "1. Ahmad\n2. Budi\n3. Siti")
        status = st.selectbox("Keterangan Default", ["Hadir", "Sakit", "Izin", "Alpa"])
        submit_presensi = st.form_submit_button("Simpan Presensi")
        if submit_presensi:
            st.success(f"Data presensi untuk {kelas} tanggal {tanggal} berhasil disimpan!")

# --- 2. DIGMA (Jurnal Mengajar) ---
elif st.session_state.current_page == 'digma':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## 📖 DIGMA: Digitalisasi Jurnal Mengajar Guru")
    st.write("Catat kegiatan belajar mengajar harian Anda di sini.")
    
    with st.form("form_jurnal"):
        tgl_jurnal = st.date_input("Tanggal Mengajar", datetime.now())
        mapel = st.text_input("Mata Pelajaran", "Matematika")
        jam_ke = st.text_input("Jam Ke-", "1 - 3")
        materi = st.text_area("Materi Pembelajaran / Kegiatan", "Pecahan dan Desimal")
        catatan = st.text_area("Catatan Kelas / Kendala", "Siswa aktif berpartisipasi.")
        submit_jurnal = st.form_submit_button("Simpan Jurnal")
        if submit_jurnal:
            st.success("Jurnal mengajar berhasil dicatat!")

# --- 3. SAKTI (Simulasi Asesmen / TKA) ---
elif st.session_state.current_page == 'sakti':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## ⚡ SAKTI: Sistem Asesmen & Kompetensi Terintegrasi")
    st.write("Simulasi Ujian / Asesmen Kompetensi Siswa SD.")
    
    nama_peserta = st.text_input("Nama Lengkap Siswa", "Siswa Contoh")
    mapel_tka = st.selectbox("Pilih Mata Ujian", ["Matematika & Numerasi", "Literasi Membaca"])
    
    st.markdown("### Soal Simulasi")
    q1 = st.radio("1. Ibu membeli 3 kg apel. Setiap kg berisi 4 buah apel. Berapa jumlah seluruh buah apel Ibu?", 
                  ["10 buah", "12 buah", "15 buah", "7 buah"])
    q2 = st.radio("2. Hasil dari 125 + 75 - 50 adalah...", 
                  ["150", "140", "160", "130"])
    
    if st.button("Kirim Jawaban Ujian"):
        nilai = 0
        if q1 == "12 buah": nilai += 50
        if q2 == "150": nilai += 50
        st.success(f"Ujian selesai! Peserta: {nama_peserta} | Skor Anda: {nilai}/100")

# --- 4. GEMA (Generator Modul Ajar) ---
elif st.session_state.current_page == 'gema':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## 📚 GEMA: Generator Modul Ajar Pembelajaran Mendalam")
    st.write("Buat draf Modul Ajar kurikulum terbaru dengan cepat dan terstruktur.")
    
    with st.form("form_gema"):
        mapel_gema = st.text_input("Mata Pelajaran / Topik Utama", "IPAS - Ekosistem")
        fase = st.selectbox("Fase / Kelas", ["Fase C / Kelas 5", "Fase C / Kelas 6"])
        tujuan = st.text_area("Tujuan Pembelajaran", "Siswa mampu memahami rantai makanan pada ekosistem sawah.")
        generate_btn = st.form_submit_button("Buat Modul Ajar")
        
        if generate_btn:
            st.markdown("---")
            st.markdown("### 📄 Hasil Draf Modul Ajar")
            st.write(f"**Topik:** {mapel_gema}")
            st.write(f"**Fase/Kelas:** {fase}")
            st.write(f"**Tujuan Pembelajaran:** {tujuan}")
            st.markdown("**Langkah Pembelajaran Mendalam:** \n1. **Pendahuluan:** Tanya jawab apersepsi mengenai hewan di sawah.\n2. **Inti:** Diskusi kelompok menyusun bagan rantai makanan.\n3. **Penutup:** Refleksi bersama dan penarikan kesimpulan.")
