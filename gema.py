"""
Modul: GEMA (Generator Modul Ajar)
Pengembang: Yustinus Budi Setyanta - Pengawas Sekolah Cabdin Bangkalan
"""

import streamlit as st
import google.generativeai as genai

def render_gema():
    st.markdown("### 🚀 GEMA: Generator Modul Ajar (Berbasis AI)")
    st.write("Susun Modul Ajar Pembelajaran Mendalam secara otomatis menggunakan kecerdasan buatan Google Gemini.")

    jenjang_pendidikan = st.selectbox(
        "Pilih Jenjang Pendidikan",
        ["SD / MI", "SMP / MTs", "SMA / MA", "SMK / MAK"]
    )

    mata_pelajaran = st.text_input("Mata Pelajaran / Program Kejuruan", "Pendidikan Pancasila")
    fase_kelas = st.selectbox("Fase / Kelas", ["Fase A", "Fase B", "Fase C", "Fase D", "Fase E", "Fase F"])
    topik = st.text_input("Topik / Materi Pokok", "Contoh: Nilai-nilai Pancasila dalam Kehidupan Sehari-hari")
    alokasi_waktu = st.text_input("Alokasi Waktu", "2 JP (2 x 45 Menit)")

    st.markdown("---")
    st.header("🏫 Identitas Satuan Pendidikan")
    nama_sekolah = st.text_input("Nama Sekolah", "SMKN 1 Bangkalan")
    nama_penulis = st.text_input("Nama Penyusun", st.session_state.get("user_nama", "Yustinus Budi Setyanta"))

    if st.button("🚀 Buat Modul Ajar GEMA", type="primary"):
        api_key = st.session_state.get("gemini_api_key", "")
        if not api_key:
            st.error("⚠️ Mohon masukkan Google Gemini API Key terlebih dahulu di menu sidebar.")
        elif not topik:
            st.warning("⚠️ Mohon isi topik pembelajaran terlebih dahulu.")
        else:
            with st.spinner("Sistem GEMA sedang menyusun Modul Ajar lengkap dengan AI..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                prompt = f"""
                Buatlah Modul Ajar Kurikulum Merdeka yang komprehensif dan mendalam untuk:
                - Jenjang: {jenjang_pendidikan}
                - Mata Pelajaran: {mata_pelajaran}
                - Fase/Kelas: {fase_kelas}
                - Topik/Materi: {topik}
                - Alokasi Waktu: {alokasi_waktu}
                - Sekolah: {nama_sekolah}
                - Penyusun: {nama_penulis}
                Berikan rancangan yang mencakup Identitas, Tujuan Pembelajaran, Langkah-langkah Pembelajaran, dan Asesmen.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.success("🎉 Modul Ajar GEMA Berhasil Disusun!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memanggil Gemini API: {e}")