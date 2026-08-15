import streamlit as st
import google.generativeai as genai
import pandas as pd

def render_sakti():
    st.markdown("### 🎯 SAKTI (Sistem Asesmen & Kompetensi Terintegrasi)")
    st.write("Sistem Asesmen & Kompetensi Terintegrasi (Pembelajaran Mendalam)")
    st.markdown("---")

    # Menggunakan Tabs agar rapi antara Pembuatan Soal dan Input Nilai Siswa
    tab1, tab2 = st.tabs(["🚀 Buat Instrumen Asesmen", "📝 Input Hasil Asesmen Siswa"])

    with tab1:
        # Form Input Parameter
        with st.expander("Parameter Pembuatan Soal & Asesmen (Pendekatan PM)", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                mapel = st.text_input("Mata Pelajaran", placeholder="Contoh: Bahasa Indonesia", key="sakti_mapel")
            with col2:
                materi = st.text_input("Materi / Topik", placeholder="Contoh: Mengidentifikasi Makna Kata", key="sakti_materi")

            col3, col4, col5 = st.columns(3)
            with col3:
                jenjang = st.selectbox("Jenjang", ["SD", "SMP", "SMA", "SMK"], index=3, key="sakti_jenjang")
            with col4:
                fase = st.selectbox("Fase", ["Fase A", "Fase B", "Fase C", "Fase D", "Fase E", "Fase F"], index=4, key="sakti_fase")
            with col5:
                kelas = st.selectbox("Kelas", [f"Kelas {i}" for i in range(1, 13)], index=9, key="sakti_kelas")

            col6, col7 = st.columns(2)
            with col6:
                jenis_asesmen = st.selectbox("Jenis Asesmen (Pendekatan PM)", ["Asesmen Formatif", "Asesmen Sumatif"], key="sakti_jenis")
            with col7:
                if jenis_asesmen == "Asesmen Formatif":
                    sub_asesmen = st.selectbox("Bentuk / Sub Jenis Asesmen", 
                        ["Tertulis - Pilihan Ganda", "Tertulis - Esai", "Tertulis - Refleksi", "Tertulis - Jurnal", "Tertulis - Kuis", "Tidak Tertulis - Diskusi", "Tidak Tertulis - Tanya-Jawab"], key="sakti_sub_formatif")
                else:
                    sub_asesmen = st.selectbox("Bentuk / Sub Jenis Asesmen", 
                        ["Sumatif Tulis", "Sumatif Lisan", "Sumatif Tugas", "Sumatif Praktik", "Sumatif Proyek", "Sumatif Produk"], key="sakti_sub_sumatif")

            col8, col9 = st.columns(2)
            with col8:
                jumlah_soal = st.number_input("Jumlah Butir Soal", min_value=1, max_value=20, value=5, key="sakti_jumlah")
            with col9:
                kesulitan = st.selectbox("Tingkat Kesulitan", ["Mudah", "Sedang", "Sulit"], index=1, key="sakti_kesulitan")

            btn_generate = st.button("✨ Buat Instrumen Asesmen dengan Gemini AI 🚀", use_container_width=True, key="btn_sakti_gen")

        # Logika Generate AI & Penyimpanan Session State untuk Download
        if btn_generate:
            if not mapel or not materi:
                st.warning("Harap isi Mata Pelajaran dan Materi terlebih dahulu!")
            else:
                with st.spinner("Sedang merancang instrumen asesmen mendalam..."):
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
                        api_key = st.session_state.get("gemini_api_key", "")
                        if not api_key:
                            st.error("API Key belum diset. Silakan masukkan di sidebar.")
                        else:
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel("gemini-3.5-flash")
                            response = model.generate_content(prompt)
                            
                            # Simpan hasil ke session_state agar tidak hilang saat interaksi lain
                            st.session_state["sakti_last_result"] = response.text
                    except Exception as e:
                        st.error(f"Gagal memanggil AI: {str(e)}")

        # Tampilkan hasil jika ada di session state + Tombol Download
        if "sakti_last_result" in st.session_state and st.session_state["sakti_last_result"]:
            st.markdown("### 📋 Hasil Instrumen Asesmen dari AI:")
            st.success("Instrumen berhasil dibuat!")
            st.markdown(st.session_state["sakti_last_result"])
            
            st.markdown("---")
            st.download_button(
                label="📥 Unduh Instrumen Asesmen (.txt)",
                data=st.session_state["sakti_last_result"],
                file_name=f"Instrumen_Asesmen_{mapel.replace(' ', '_')}.txt" if 'mapel' in locals() and mapel else "Instrumen_Asesmen.txt",
                mime="text/plain",
                key="download_instrumen_txt"
            )

    with tab2:
        st.subheader("📝 Lembar Input Hasil Asesmen Siswa")
        st.write("Catat dan rekap nilai hasil asesmen formatif atau sumatif peserta didik.")

        with st.form("form_input_nilai", clear_on_submit=True):
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                nama_siswa = st.text_input("Nama Lengkap Siswa")
                nis_siswa = st.text_input("NIS / NISN (Opsional)")
            with col_n2:
                jenis_penilaian = st.selectbox("Jenis Asesmen yang Diinput", ["Formatif - Kuis/Tugas", "Sumatif Tulis", "Sumatif Praktik/Proyek", "Sumatif Produk"])
                nilai_siswa = st.number_input("Nilai Akhir (Skala 0 - 100)", min_value=0.0, max_value=100.0, value=75.0, step=0.5)
            
            catatan_guru = st.text_area("Catatan Perkembangan / Umpan Balik (Feedback)")
            submit_nilai = st.form_submit_button("💾 Simpan Hasil Asesmen Siswa")

        if submit_nilai:
            if not nama_siswa:
                st.warning("Nama siswa wajib diisi!")
            else:
                if "sakti_data_nilai" not in st.session_state:
                    st.session_state["sakti_data_nilai"] = []
                
                st.session_state["sakti_data_nilai"].append({
                    "Nama Siswa": nama_siswa,
                    "NIS": nis_siswa if nis_siswa else "-",
                    "Jenis Asesmen": jenis_penilaian,
                    "Nilai": nilai_siswa,
                    "Catatan": catatan_guru if catatan_guru else "-"
                })
                st.success(f"Hasil asesmen untuk **{nama_siswa}** berhasil disimpan ke rekap!")

        # Menampilkan Tabel Rekap Nilai
        if "sakti_data_nilai" in st.session_state and st.session_state["sakti_data_nilai"]:
            st.markdown("---")
            st.subheader("📊 Tabel Rekapitulasi Hasil Asesmen Kelas")
            df_nilai = pd.DataFrame(st.session_state["sakti_data_nilai"])
            st.dataframe(df_nilai, use_container_width=True)

            # Tombol Download Rekap Nilai CSV
            csv_data = df_nilai.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Unduh Rekap Nilai (.csv)",
                data=csv_data,
                file_name="Rekapitulasi_Hasil_Asesmen_Sakti.csv",
                mime="text/csv",
                key="download_rekap_csv"
            )
        else:
            st.info("Belum ada data nilai siswa yang diinput.")