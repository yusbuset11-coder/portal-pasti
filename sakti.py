import streamlit as st
import google.generativeai as genai
import pandas as pd
import io
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def render_sakti():
    st.markdown("### 🎯 SAKTI (Sistem Asesmen & Kompetensi Terintegrasi)")
    st.write("Sistem Asesmen & Kompetensi Terintegrasi (Pembelajaran Mendalam)")

    # Form Pembuatan Soal & Asesmen (AI)
    with st.expander("✨ Parameter Pembuatan Soal & Asesmen (Pendekatan PM)", expanded=False):
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
                        
                        st.markdown("### 📋 Hasil Instrumen Asesmen dari AI:")
                        st.success("Instrumen berhasil dibuat!")
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"Gagal memanggil AI: {str(e)}")

    st.markdown("---")

    # Lembar Input Hasil Asesmen Siswa
    st.markdown("### 📄 Lembar Input Hasil Asesmen Siswa")
    st.write("Catat dan rekap nilai hasil asesmen formatif atau sumatif peserta didik.")

    with st.form("form_input_asesmen_sakti"):
        col_a, col_b = st.columns(2)
        with col_a:
            nama_siswa = st.text_input("Nama Lengkap Siswa", placeholder="Masukkan nama lengkap peserta didik")
            nis_siswa = st.text_input("NIS / NISN (Opsional)", placeholder="Nomor Induk Siswa")
        with col_b:
            jenis_penilaian = st.selectbox("Jenis Asesmen yang Diinput", [
                "Formatif - Kuis/Tugas",
                "Formatif - Tertulis Pilihan Ganda",
                "Formatif - Tertulis Esai",
                "Formatif - Refleksi / Jurnal",
                "Sumatif Tulis",
                "Sumatif Praktik",
                "Sumatif Proyek",
                "Sumatif Produk"
            ])
            nilai_siswa = st.number_input("Nilai Akhir (Skala 0 - 100)", min_value=0.0, max_value=100.0, value=75.0, step=0.25)
        
        catatan_guru = st.text_area("Catatan Perkembangan / Umpan Balik (Feedback)", placeholder="Tuliskan catatan kualitatif atau umpan balik...")

        submitted = st.form_submit_button("💾 Simpan Hasil Asesmen Siswa")

        if submitted:
            if not nama_siswa.strip():
                st.error("❌ Nama Lengkap Siswa wajib diisi sebelum menyimpan data!")
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
                st.success(f"✅ Hasil asesmen untuk **{nama_siswa}** berhasil disimpan!")

    # Fungsi untuk membuat file Excel yang rapi dengan openpyxl
    def generate_styled_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Rekap Asesmen')
            workbook = writer.book
            worksheet = writer.sheets['Rekap Asesmen']
            
            # Styling Header
            header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
            header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            align_center = Alignment(horizontal="center", vertical="center")
            thin_border = Border(
                left=Side(style='thin', color='D9D9D9'),
                right=Side(style='thin', color='D9D9D9'),
                top=Side(style='thin', color='D9D9D9'),
                bottom=Side(style='thin', color='D9D9D9')
            )
            
            for col_num in range(1, len(df.columns) + 1):
                cell = worksheet.cell(row=1, column=col_num)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = align_center
            
            # Styling Baris Data
            for row in range(2, len(df) + 2):
                for col in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=row, column=col)
                    cell.border = thin_border
                    cell.alignment = Alignment(vertical="center")
                    
            # Otomatis sesuaikan lebar kolom
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                worksheet.column_dimensions[col_letter].width = max(max_len + 4, 15)
                
        output.seek(0)
        return output.getvalue()

    # Menampilkan Tabel Rekap Nilai
    if "sakti_data_nilai" in st.session_state and st.session_state["sakti_data_nilai"]:
        st.markdown("---")
        st.subheader("📊 Tabel Rekapitulasi Hasil Asesmen Kelas")
        df_nilai = pd.DataFrame(st.session_state["sakti_data_nilai"])
        st.dataframe(df_nilai, use_container_width=True)

        # Tombol Download Rekap Nilai Excel (.xlsx)
        excel_data = generate_styled_excel(df_nilai)
        st.download_button(
            label="📥 Unduh Rekap Nilai (Excel .xlsx)",
            data=excel_data,
            file_name="Rekapitulasi_Hasil_Asesmen_Sakti.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_rekap_excel"
        )
    else:
        st.info("ℹ️ Belum ada data nilai siswa yang diinput.")