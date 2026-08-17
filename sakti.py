"""
Modul: SAKTI (Sistem Asesmen & Kompetensi Terintegrasi)
Pengembang: Yustinus Budi Setyanta
"""

import streamlit as st
import pandas as pd

def render_sakti():
    st.markdown("### 🎯 SAKTI: Sistem Asesmen & Kompetensi Terintegrasi")
    st.write("Kelola data asesmen, penilaian kompetensi, dan analisis hasil belajar siswa secara komprehensif.")

    # Pembagian Tab untuk Navigasi SAKTI
    tab1, tab2, tab3 = st.tabs([
        "📝 Input Nilai Asesmen", 
        "📊 Analisis Kompetensi", 
        "📥 Ekspor Hasil Asesmen"
    ])

    with tab1:
        st.markdown("#### Form Input Nilai Asesmen Siswa")
        col1, col2 = st.columns(2)
        with col1:
            kelas_pilih = st.selectbox("📚 Pilih Kelas:", ["Kelas X", "Kelas XI", "Kelas XII"], key="sakti_kelas")
            jenis_asesmen = st.selectbox("📋 Jenis Asesmen:", ["Formatif 1", "Sumatif Tengah Semester", "Sumatif Akhir Semester"], key="sakti_jenis")
        with col2:
            mata_pelajaran = st.text_input("📖 Mata Pelajaran", value="Pendidikan Pancasila", key="sakti_mapel")
            kktp = st.number_input("🎯 Nilai KKTP (Kriteria Ketercapaian Tujuan Pembelajaran)", value=75, min_value=0, max_value=100)

        # Data dummy siswa untuk asesmen
        df_asesmen = pd.DataFrame({
            "ID_Siswa": [101, 102, 103],
            "Nama_Siswa": ["Ahmad Fauzi", "Siti Aminah", "Budi Santoso"],
            "Nilai": [80, 70, 85]
        })

        edited_asesmen = st.data_editor(
            df_asesmen,
            column_config={
                "ID_Siswa": st.column_config.NumberColumn("ID", disabled=True),
                "Nama_Siswa": st.column_config.TextColumn("Nama Siswa", disabled=True),
                "Nilai": st.column_config.NumberColumn("Nilai Akhir", min_value=0, max_value=100, step=1)
            },
            hide_index=True,
            use_container_width=True
        )

        if st.button("💾 Simpan Nilai Asesmen", type="primary"):
            st.success("✅ Nilai asesmen berhasil disimpan ke database SAKTI!")

    with tab2:
        st.markdown("#### Analisis Pencapaian Kompetensi")
        st.info("Grafik dan rekapitulasi ketuntasan belajar siswa berdasarkan KKTP.")
        
        df_analisis = pd.DataFrame({
            "Kategori": ["Tuntas (>= KKTP)", "Belum Tuntas (< KKTP)"],
            "Jumlah Siswa": [28, 5]
        })
        st.bar_chart(df_analisis.set_index("Kategori"))

    with tab3:
        st.markdown("#### Ekspor Rekapitulasi Nilai")
        st.write("Unduh laporan rekapitulasi nilai asesmen lengkap dalam format Excel.")
        if st.button("📥 Download Rekap Nilai (Excel)"):
            st.info("File rekapitulasi nilai sedang disiapkan untuk diunduh...")