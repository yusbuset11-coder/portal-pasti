import streamlit as st
import google.generativeai as genai

def render_sakti():
    st.markdown("### 🎯 SAKTI (Sistem Asesmen & Kompetensi Terintegrasi)")
    st.write("Sistem Asesmen & Kompetensi Terintegrasi (Pembelajaran Mendalam)")

    # Form Input
    with st.expander("Parameter Pembuatan Soal & Asesmen (Pendekatan PM)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            mapel = st.text_input("Mata Pelajaran", placeholder="Contoh: Bahasa Indonesia")
        with col2:
            materi = st.text_input("Materi / Topik", placeholder="Contoh: Mengidentifikasi Makna Kata")

        col3, col4, col5 = st.columns(3)
        with col3:
            jenjang = st.selectbox("Jenjang", ["SD", "SMP", "SMA", "SMK"], index=3)
        with col4:
            fase = st.selectbox("Fase", ["Fase A", "Fase B", "Fase C", "Fase D", "Fase E", "Fase F"], index=4)
        with col5:
            kelas = st.selectbox("Kelas", [f"Kelas {i}" for i in range(1, 13)], index=9)

        col6, col7 = st.columns(2)
        with col6:
            jenis_asesmen = st.selectbox("Jenis Asesmen (Pendekatan PM)", ["Asesmen Formatif", "Asesmen Sumatif"])
        
        with col7:
            if jenis_asesmen == "Asesmen Formatif":
                sub_asesmen = st.selectbox("Bentuk / Sub Jenis Asesmen", 
                    ["Tertulis - Pilihan Ganda", "Tertulis - Esai", "Tertulis - Refleksi", "Tertulis - Jurnal", "Tertulis - Kuis", "Tidak Tertulis - Diskusi", "Tidak Tertulis - Tanya-Jawab"])
            else:
                sub_asesmen = st.selectbox("Bentuk / Sub Jenis Asesmen", 
                    ["Sumatif Tulis", "Sumatif Lisan", "Sumatif Tugas", "Sumatif Praktik", "Sumatif Proyek", "Sumatif Produk"])

        col8, col9 = st.columns(2)
        with col8:
            jumlah_soal = st.number_input("Jumlah Butir Soal", min_value=1, max_value=20, value=5)
        with col9:
            kesulitan = st.selectbox("Tingkat Kesulitan", ["Mudah", "Sedang", "Sulit"], index=1)

        btn_generate = st.button("✨ Buat Instrumen Asesmen dengan Gemini AI 🚀", use_container_width=True)

    # Logika Generate AI
    if btn_generate:
        if not mapel or not materi:
            st.warning("Harap isi Mata Pelajaran dan Materi terlebih dahulu!")
        else:
            with st.spinner("Sedang merancang instrumen asesmen mendalam..."):
                # Aturan Opsi
                aturan_opsi = "3 opsi (A sampai C)" if jenjang == "SD" else ("4 opsi (A sampai D)" if jenjang == "SMP" else "5 opsi (A sampai E)")
                
                prompt = f"""
                Buatkan instrumen asesmen dengan pendekatan Pembelajaran Mendalam (PM).
                Mata Pelajaran: {mapel}
                Materi: {materi}
                Jenjang: {jenjang}
                Fase: {fase}
                Kelas: {kelas}
                Jenis Asesmen: {jenis_asesmen}
                Sub Jenis: {sub_asesmen}
                Jumlah Soal: {jumlah_soal}
                Tingkat Kesulitan: {kesulitan}
                Aturan Pilihan Ganda: {aturan_opsi}
                
                Mohon berikan format yang rapi dan profesional untuk digunakan di sekolah.
                """
                
                try:
                    # Menggunakan API Key dari st.session_state (pastikan sudah diset di app.py)
                    api_key = st.session_state.get("gemini_api_key", "")
                    if not api_key:
                        st.error("API Key belum diset. Silakan masukkan di sidebar.")
                    else:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        response = model.generate_content(prompt)
                        
                        st.markdown("### 📋 Hasil Instrumen Asesmen dari AI:")
                        st.success("Instrumen berhasil dibuat!")
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"Gagal memanggil AI: {str(e)}")

# Panggil fungsi ini di app.py Anda