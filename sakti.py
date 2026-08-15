import streamlit as st
import google.generativeai as genai
import pandas as pd
import io
import datetime
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def render_sakti():
    st.markdown("### 🎯 SAKTI (Sistem Asesmen & Kompetensi Terintegrasi)")
    st.write("Sistem Asesmen & Kompetensi Terintegrasi (Pembelajaran Mendalam)")

    # Inisialisasi Database Siswa di Session State (untuk Nama Otomatis berdasarkan No Absen & Kelas)
    if "db_siswa" not in st.session_state:
        st.session_state["db_siswa"] = {
            ("Kelas 10", 1): "Ahmad Fauzi",
            ("Kelas 10", 2): "Bunga Citra",
            ("Kelas 10", 3): "Candra Wijaya",
            ("Kelas 10", 4): "Dewi Lestari",
            ("Kelas 10", 5): "Eko Prasetyo",
            ("Kelas 11", 1): "Fajar Nugraha",
            ("Kelas 11", 2): "Gita Savitri",
            ("Kelas 11", 3): "Hadi Pratama",
        }

    # Form Pembuatan Soal & Asesmen (AI)
    with st.expander("✨ Parameter Pembuatan Soal & Asesmen (Pendekatan PM)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            mapel_ai = st.text_input("Mata Pelajaran (AI)", placeholder="Contoh: Bahasa Indonesia")
        with col2:
            materi_ai = st.text_input("Materi / Topik (AI)", placeholder="Contoh: Mengidentifikasi Makna Kata")

        col3, col4, col5 = st.columns(3)
        with col3:
            jenjang_ai = st.selectbox("Jenjang (AI)", ["SD", "SMP", "SMA", "SMK"], index=3)
        with col4:
            fase_ai = st.selectbox("Fase (AI)", ["Fase A", "Fase B", "Fase C", "Fase D", "Fase E", "Fase F"], index=4)
        with col5:
            kelas_ai = st.selectbox("Kelas (AI)", [f"Kelas {i}" for i in range(1, 13)], index=9)

        col6, col7 = st.columns(2)
        with col6:
            jenis_asesmen_ai = st.selectbox("Jenis Asesmen (AI)", ["Asesmen Formatif", "Asesmen Sumatif"])
        with col7:
            if jenis_asesmen_ai == "Asesmen Formatif":
                sub_asesmen_ai = st.selectbox("Sub Jenis Asesmen (AI)", ["Tertulis", "Tak Tertulis"])
            else:
                sub_asesmen_ai = st.selectbox("Sub Jenis Asesmen (AI)", ["Lisan", "Tulis", "Tugas", "Praktik", "Proyek", "Produk"])

        col8, col9 = st.columns(2)
        with col8:
            jumlah_soal = st.number_input("Jumlah Butir Soal", min_value=1, max_value=20, value=5)
        with col9:
            kesulitan = st.selectbox("Tingkat Kesulitan", ["Mudah", "Sedang", "Sulit"], index=1)

        btn_generate = st.button("✨ Buat Instrumen Asesmen dengan Gemini AI 🚀", use_container_width=True)

    if btn_generate:
        if not mapel_ai or not materi_ai:
            st.warning("Harap isi Mata Pelajaran dan Materi terlebih dahulu!")
        else:
            with st.spinner("Sedang merancang instrumen asesmen mendalam..."):
                aturan_opsi = "3 opsi (A sampai C)" if jenjang_ai == "SD" else ("4 opsi (A sampai D)" if jenjang_ai == "SMP" else "5 opsi (A sampai E)")
                prompt = f"""
                Buatkan instrumen asesmen dengan pendekatan Pembelajaran Mendalam (PM).
                Mata Pelajaran: {mapel_ai}, Materi: {materi_ai}, Jenjang: {jenjang_ai}, Fase: {fase_ai}, Kelas: {kelas_ai}, 
                Jenis Asesmen: {jenis_asesmen_ai}, Sub Jenis: {sub_asesmen_ai}, Jumlah Soal: {jumlah_soal}, Tingkat Kesulitan: {kesulitan}, Aturan Pilihan Ganda: {aturan_opsi}
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

    # Expand untuk Tambah/Kelola Data Siswa Roster Kelas
    with st.expander("⚙️ Kelola / Tambah Data Nama Siswa per Kelas"):
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            m_kelas = st.selectbox("Pilih Kelas Roster", [f"Kelas {i}" for i in range(1, 13)], index=9, key="m_kls")
        with col_m2:
            m_absen = st.number_input("Nomor Absen", min_value=1, max_value=50, value=1, key="m_abs")
        with col_m3:
            m_nama = st.text_input("Nama Lengkap Siswa", key="m_nms")
        
        if st.button("➕ Tambahkan/Update Siswa ke Master Roster"):
            if m_nama.strip():
                st.session_state["db_siswa"][(m_kelas, int(m_absen))] = m_nama.strip()
                st.success(f"Berhasil mendaftarkan **{m_nama}** (Absen {m_absen}) di {m_kelas}!")
            else:
                st.warning("Nama siswa tidak boleh kosong.")

    st.markdown("### 📄 Lembar Input Hasil Asesmen Siswa")
    st.write("Catat dan rekap nilai hasil asesmen formatif atau sumatif peserta didik.")

    # Form Input Sesuai Alur
    with st.form("form_input_asesmen_sakti"):
        col_a, col_b = st.columns(2)
        with col_a:
            nama_sekolah = st.text_input("Asal Sekolah", placeholder="Masukkan nama sekolah")
            tanggal_input = st.date_input("Tanggal", value=datetime.date.today())
            nama_guru = st.text_input("Nama Guru", placeholder="Masukkan nama guru pengampu")
            mata_pelajaran = st.text_input("Mata Pelajaran", placeholder="Masukkan mata pelajaran")
            jenjang_kelas = st.selectbox("Pilih Jenjang", ["SD", "SMP", "SMA", "SMK"], index=3)
            pilih_kelas = st.selectbox("Pilih Kelas", [f"Kelas {i}" for i in range(1, 13)], index=9)
            
        with col_b:
            jenis_asesmen = st.selectbox("Jenis Asesmen", ["Formatif", "Sumatif"])
            
            if jenis_asesmen == "Formatif":
                sub_jenis_asesmen = st.selectbox("Sub Jenis Asesmen", ["Tertulis", "Tak Tertulis"])
            else:
                sub_jenis_asesmen = st.selectbox("Sub Jenis Asesmen", ["Lisan", "Tulis", "Tugas", "Praktik", "Proyek", "Produk"])
                
            materi_topik = st.text_input("Ketik Materi", placeholder="Masukkan materi pembelajaran")
            no_absen = st.number_input("Ketik Nomor Absen", min_value=1, max_value=50, value=1)
            
            # Otomatis mengambil nama siswa berdasarkan Kelas dan Nomor Absen
            nama_siswa_otomatis = st.session_state["db_siswa"].get((pilih_kelas, int(no_absen)), "")
            nama_siswa = st.text_input("Nama Siswa (Muncul Otomatis / Edit Manual)", value=nama_siswa_otomatis, placeholder="Nama siswa muncul otomatis...")

        col_c, col_d = st.columns(2)
        with col_c:
            nis_siswa = st.text_input("NIS / NISN (Opsional)", placeholder="Nomor Induk Siswa")
        with col_d:
            nilai_siswa = st.number_input("Ketik Nilai Akhir (Skala 0 - 100)", min_value=0.0, max_value=100.0, value=75.0, step=0.25)
        
        catatan_guru = st.text_area("Catatan Perkembangan / Umpan Balik (Feedback)", placeholder="Tuliskan catatan kualitatif atau umpan balik...")

        submitted = st.form_submit_button("💾 Simpan Nilai Asesmen")

        if submitted:
            if not nama_siswa.strip() or not nama_guru.strip() or not nama_sekolah.strip():
                st.error("❌ Asal Sekolah, Nama Guru, dan Nama Siswa wajib diisi sebelum menyimpan data!")
            else:
                if "sakti_data_nilai" not in st.session_state:
                    st.session_state["sakti_data_nilai"] = []
                
                st.session_state["sakti_data_nilai"].append({
                    "Sekolah": nama_sekolah,
                    "Tanggal": str(tanggal_input),
                    "Guru Pengampu": nama_guru,
                    "Mata Pelajaran": mata_pelajaran,
                    "Jenjang": jenjang_kelas,
                    "Kelas": pilih_kelas,
                    "Jenis Asesmen": jenis_asesmen,
                    "Sub Jenis Asesmen": sub_jenis_asesmen,
                    "Materi": materi_topik,
                    "No Absen": no_absen,
                    "Nama Siswa": nama_siswa,
                    "NIS": nis_siswa if nis_siswa else "-",
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
            
            header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
            header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            align_center = Alignment(horizontal="center", vertical="center")
            thin_border = Border(
                left=Side(style='thin', color='D9D9D9'), right=Side(style='thin', color='D9D9D9'),
                top=Side(style='thin', color='D9D9D9'), bottom=Side(style='thin', color='D9D9D9')
            )
            
            for col_num in range(1, len(df.columns) + 1):
                cell = worksheet.cell(row=1, column=col_num)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = align_center
            
            for row in range(2, len(df) + 2):
                for col in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=row, column=col)
                    cell.border = thin_border
                    cell.alignment = Alignment(vertical="center")
                    
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                worksheet.column_dimensions[col_letter].width = max(max_len + 4, 15)
                
        output.seek(0)
        return output.getvalue()

    # Menampilkan Tabel Rekap Nilai & Filter Berdasarkan Sekolah, Kelas, dan Mata Pelajaran
    if "sakti_data_nilai" in st.session_state and st.session_state["sakti_data_nilai"]:
        st.markdown("---")
        st.subheader("📊 Tabel Rekapitulasi Hasil Asesmen Kelas")
        
        df_all = pd.DataFrame(st.session_state["sakti_data_nilai"])

        # Filter Section: Sekolah, Kelas, Mata Pelajaran
        st.markdown("#### 🔍 Filter Rekapitulasi Data")
        f_col1, f_col2, f_col3 = st.columns(3)
        
        list_sekolah = ["Semua Sekolah"] + sorted(df_all["Sekolah"].unique().tolist())
        list_kelas = ["Semua Kelas"] + sorted(df_all["Kelas"].unique().tolist())
        list_mapel = ["Semua Mata Pelajaran"] + sorted(df_all["Mata Pelajaran"].unique().tolist())

        with f_col1:
            pilih_filter_sekolah = st.selectbox("Filter Sekolah", list_sekolah)
        with f_col2:
            pilih_filter_kelas = st.selectbox("Filter Kelas", list_kelas)
        with f_col3:
            pilih_filter_mapel = st.selectbox("Filter Mata Pelajaran", list_mapel)

        # Terapkan Filter ke DataFrame
        df_filtered = df_all.copy()
        if pilih_filter_sekolah != "Semua Sekolah":
            df_filtered = df_filtered[df_filtered["Sekolah"] == pilih_filter_sekolah]
        if pilih_filter_kelas != "Semua Kelas":
            df_filtered = df_filtered[df_filtered["Kelas"] == pilih_filter_kelas]
        if pilih_filter_mapel != "Semua Mata Pelajaran":
            df_filtered = df_filtered[df_filtered["Mata Pelajaran"] == pilih_filter_mapel]

        st.dataframe(df_filtered, use_container_width=True)

        # Tombol Download Rekap Nilai Excel (.xlsx) berdasarkan data yang difilter
        if not df_filtered.empty:
            excel_data = generate_styled_excel(df_filtered)
            st.download_button(
                label="📥 Unduh Rekap Nilai Terfiltrasi (Excel .xlsx)",
                data=excel_data,
                file_name="Rekapitulasi_Hasil_Asesmen_Sakti.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_rekap_excel"
            )
        else:
            st.info("ℹ️ Tidak ada data yang sesuai dengan filter yang dipilih.")
    else:
        st.info("ℹ️ Belum ada data nilai siswa yang diinput.")