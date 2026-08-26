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

def go_to(page_name):
    st.session_state.current_page = page_name

# --- BERANDA / DASHBOARD UTAMA ---
if st.session_state.current_page == 'home':
    # Banner Biru Utama
    st.markdown("""
        <div style="background-color: #0284c7; padding: 35px; border-radius: 10px; text-align: center; color: white; margin-bottom: 30px;">
            <h1 style="margin: 0; color: white; font-size: 40px;">📁 PASTI</h1>
            <p style="margin: 10px 0 0 0; color: #e0f2fe; font-size: 18px;">Portal Akademik Siswa Terintegrasi</p>
        </div>
    """, unsafe_allow_html=True)

    # 4 Kotak Menu Utama
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>👤</h3>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>SIPENSIS</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 14px;'>Sistem Informasi Presensi Siswa.</p>", unsafe_allow_html=True)
            if st.button("Buka SIPENSIS", use_container_width=True, key="btn_sipensis"):
                go_to('sipensis')

    with col2:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>📖</h3>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>DIGMA</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 14px;'>Digitalisasi Jurnal Mengajar Guru.</p>", unsafe_allow_html=True)
            if st.button("Buka DIGMA", use_container_width=True, key="btn_digma"):
                go_to('digma')

    with col3:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>⚡</h3>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>SAKTI</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 14px;'>Sistem Asesmen & Kompetensi Terintegrasi.</p>", unsafe_allow_html=True)
            if st.button("Buka SAKTI", use_container_width=True, key="btn_sakti"):
                go_to('sakti')

    with col4:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>📚</h3>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #0284c7;'>GEMA</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 14px;'>Generator Modul Ajar Pembelajaran Mendalam.</p>", unsafe_allow_html=True)
            if st.button("Buka GEMA", use_container_width=True, key="btn_gema"):
                go_to('gema')
            
    st.write("---")
    if st.button("🚪 Keluar (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

# --- HALAMAN SIPENSIS ---
elif st.session_state.current_page == 'sipensis':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## 👤 SIPENSIS: Sistem Informasi Presensi Siswa")
    st.write("Gunakan halaman ini untuk mencatat dan merekap kehadiran siswa.")
    with st.form("form_presensi"):
        kelas = st.selectbox("Pilih Kelas", ["Kelas 5A", "Kelas 5B", "Kelas 6A", "Kelas 6B"])
        tanggal = st.date_input("Tanggal Presensi", datetime.now())
        nama_siswa = st.text_area("Daftar Siswa", "1. Ahmad\n2. Budi\n3. Siti")
        status = st.selectbox("Keterangan Default", ["Hadir", "Sakit", "Izin", "Alpa"])
        if st.form_submit_button("Simpan Presensi"):
            st.success(f"Data presensi untuk {kelas} berhasil disimpan!")

# --- HALAMAN DIGMA ---
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
        if st.form_submit_button("Simpan Jurnal"):
            st.success("Jurnal mengajar berhasil dicatat!")

# --- HALAMAN SAKTI ---
elif st.session_state.current_page == 'sakti':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## ⚡ SAKTI: Sistem Asesmen & Kompetensi Terintegrasi")
    st.write("Simulasi Ujian / Asesmen Kompetensi Siswa SD.")
    nama_peserta = st.text_input("Nama Lengkap Siswa", "Siswa Contoh")
    mapel_tka = st.selectbox("Pilih Mata Ujian", ["Matematika & Numerasi", "Literasi Membaca"])
    q1 = st.radio("1. Ibu membeli 3 kg apel. Setiap kg berisi 4 buah apel. Berapa jumlah seluruh buah apel Ibu?", ["10 buah", "12 buah", "15 buah", "7 buah"])
    q2 = st.radio("2. Hasil dari 125 + 75 - 50 adalah...", ["150", "140", "160", "130"])
    if st.button("Kirim Jawaban Ujian"):
        nilai = 50 if q1 == "12 buah" else 0
        if q2 == "150": nilai += 50
        st.success(f"Ujian selesai! Skor Anda: {nilai}/100")

# --- HALAMAN GEMA ---
elif st.session_state.current_page == 'gema':
    if st.button("⬅️ Kembali ke Beranda Portal PASTI"):
        go_to('home')
    st.markdown("## 📚 GEMA: Generator Modul Ajar Pembelajaran Mendalam")
    st.write("Buat draf Modul Ajar kurikulum terbaru dengan cepat dan terstruktur.")
    with st.form("form_gema"):
        mapel_gema = st.text_input("Mata Pelajaran / Topik Utama", "IPAS - Ekosistem")
        fase = st.selectbox("Fase / Kelas", ["Fase C / Kelas 5", "Fase C / Kelas 6"])
        tujuan = st.text_area("Tujuan Pembelajaran", "Siswa mampu memahami rantai makanan pada ekosistem sawah.")
        if st.form_submit_button("Buat Modul Ajar"):
            st.markdown("---")
            st.markdown("### 📄 Hasil Draf Modul Ajar")
            st.write(f"**Topik:** {mapel_gema} | **Fase:** {fase}")
            st.write(f"**Tujuan:** {tujuan}")
