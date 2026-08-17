"""
Modul: SIPENSIS (Sistem Informasi Presensi Siswa) - Pure Supabase Fix
Pengembang: Yustinus Budi Setyanta
"""

import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client

def get_supabase_client():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def render_sipensis():
    st.markdown("### 📋 SIPENSIS: Sistem Informasi Presensi Siswa")
    
    current_email = st.session_state.get("user_email", "")
    current_sekolah = st.session_state.get("user_sekolah", "")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "✍️ Input Manual", 
        "📁 Download & Upload Excel", 
        "📊 Laporan Harian", 
        "📈 Rekap Semester Ganjil", 
        "📈 Rekap Semester Genap"
    ])

    supabase = get_supabase_client()

    with tab1:
        st.markdown("#### Form Input Presensi Harian")
        try:
            res_siswa = supabase.table("siswa").select("*").eq("user_email", current_email).execute()
            df_siswa = pd.DataFrame(res_siswa.data)
        except Exception as e:
            st.error(f"Gagal memuat data siswa: {e}")
            df_siswa = pd.DataFrame()
        
        if not df_siswa.empty:
            col1, col2 = st.columns(2)
            with col1:
                tanggal_absensi = st.date_input("📅 Tanggal Absensi", value=date.today(), key="tgl_man")
                daftar_kelas = df_siswa["kelas"].dropna().unique().tolist() if "kelas" in df_siswa.columns else ["X"]
                kelas_pilih = st.selectbox("📚 Pilih Kelas:", daftar_kelas, key="kls_man")
            
            with col2:
                nama_guru = st.text_input("👨‍🏫 Nama Guru", value=st.session_state.get("user_nama", ""), key="g_man")
                mata_pelajaran = st.text_input("📖 Mata Pelajaran", value="Pendidikan Pancasila", key="m_man")

            df_filtered = df_siswa[df_siswa["kelas"] == kelas_pilih].copy()
            st.info(f"🏫 **Sekolah Anda:** {current_sekolah}")

            if not df_filtered.empty:
                df_input = df_filtered[["id_siswa", "nama_siswa"]].copy()
                df_input["S"] = False
                df_input["I"] = False
                df_input["A"] = False

                edited_df = st.data_editor(
                    df_input,
                    column_config={
                        "id_siswa": st.column_config.TextColumn("ID Siswa", disabled=True),
                        "nama_siswa": st.column_config.TextColumn("Nama Siswa", disabled=True),
                        "S": st.column_config.CheckboxColumn("Sakit (S)"),
                        "I": st.column_config.CheckboxColumn("Izin (I)"),
                        "A": st.column_config.CheckboxColumn("Alpha (A)"),
                    },
                    hide_index=True,
                    use_container_width=True
                )

                if st.button("💾 Simpan Absensi Harian (Supabase)", type="primary"):
            # Tambahkan baris pemantau di sini
            st.write("🔍 Debug - Email aktif:", current_email)
            st.write("🔍 Debug - Sekolah aktif:", current_sekolah)
            
            with st.spinner("Menyimpan ke Supabase..."):
                try:
                    records_to_insert = []
                    for _, row in edited_df.iterrows():
                        status = "Hadir"
                        if row["S"]: status = "Sakit"
                        elif row["I"]: status = "Izin"
                        elif row["A"]: status = "Alpha"
                        
                        records_to_insert.append({
                            "tanggal": str(tanggal_absensi),
                            "sekolah": current_sekolah,
                            "user_email": current_email,
                            "nama_guru": nama_guru,
                            "mata_pelajaran": mata_pelajaran,
                            "kelas": kelas_pilih,
                            "id_siswa": str(row["id_siswa"]),
                            "nama_siswa": str(row["nama_siswa"]),
                            "status_kehadiran": status
                        })

                    # Pantau data yang akan dikirim
                    st.write("🔍 Debug - Data yang mau dikirim:", records_to_insert)

                    # Eksekusi kirim ke Supabase
                    response = supabase.table("absensi_harian").insert(records_to_insert).execute()
                    
                    # Pantau respon dari Supabase
                    st.write("🔍 Debug - Respon dari Supabase:", response)
                    
                    st.success("✅ Absensi Berhasil Disimpan ke Supabase!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Gagal menyimpan ke database: {e}")
            else:
                st.warning("Tidak ada data siswa untuk kelas tersebut.")
        else:
            st.warning("⚠️ Belum ada data siswa Anda di Supabase. Silakan unggah melalui tab 'Download & Upload Excel'.")

    with tab2:
        st.markdown("#### Manajemen Data Siswa Mandiri")
        uploaded_file = st.file_uploader("Pilih Berkas Excel Data Siswa (.xlsx)", type=["xlsx"])
        if uploaded_file is not None:
            df_upload = pd.read_excel(uploaded_file)
            st.dataframe(df_upload.head(), use_container_width=True)
            
            if st.button("🚀 Unggah ke Supabase Saya", type="primary"):
                with st.spinner("Mengunggah data..."):
                    try:
                        supabase.table("siswa").delete().eq("user_email", current_email).execute()
                        records = []
                        for _, row in df_upload.iterrows():
                            records.append({
                                "user_email": current_email,
                                "sekolah": str(row.get("Sekolah", current_sekolah)),
                                "id_siswa": str(row.get("ID_Siswa", "")),
                                "nama_siswa": str(row.get("Nama_Siswa", "")),
                                "kelas": str(row.get("Kelas", "X"))
                            })
                        supabase.table("siswa").insert(records).execute()
                        st.success("✅ Data siswa berhasil diperbarui di Supabase!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal mengunggah: {e}")

    with tab3:
        st.markdown("#### Laporan Harian Kehadiran")
        try:
            res_lap = supabase.table("absensi_harian").select("*").eq("user_email", current_email).execute()
            df_lap = pd.DataFrame(res_lap.data)
            if not df_lap.empty:
                st.dataframe(df_lap, use_container_width=True)
            else:
                st.info("Data absensi belum tersedia untuk akun ini.")
        except Exception as e:
            st.error(f"Gagal memuat laporan: {e}")

    with tab4:
        st.markdown("#### Rekapitulasi Semester Ganjil")
    with tab5:
        st.markdown("#### Rekapitulasi Semester Genap")