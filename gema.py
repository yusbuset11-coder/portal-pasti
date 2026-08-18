import streamlit as st
import google.generativeai as genai

# Tambahkan konfigurasi halaman agar identitas aplikasi jelas
st.set_page_config(page_title="GEMA - Generator Modul Ajar", layout="wide")

def render_gema():
    st.markdown("### 🚀 GEMA: Generator Modul Ajar (Berbasis AI)")
    st.write("Susun Modul Ajar Pembelajaran Mendalam secara otomatis.")

    # Input parameter di main area
    jenjang_pendidikan = st.selectbox(
        "Pilih Jenjang Pendidikan",
        ["SD / MI", "SMP / MTs", "SMA / MA", "SMK / MAK"]
    )
    mata_pelajaran = st.text_input("Mata Pelajaran", "Pendidikan Pancasila")
    fase_kelas = st.selectbox("Fase / Kelas", ["Fase A", "Fase B", "Fase C", "Fase D", "Fase E", "Fase F"])
    topik = st.text_input("Topik / Materi Pokok", "Contoh: Nilai-nilai Pancasila")
    alokasi_waktu = st.text_input("Alokasi Waktu", "2 JP (2 x 45 Menit)")

    nama_sekolah = st.text_input("Nama Sekolah", "SMKN 1 Bangkalan")
    nama_penulis = st.text_input("Nama Penyusun", "Yustinus Budi Setyanta")

    if st.button("🚀 Buat Modul Ajar GEMA", type="primary"):
        # Mengambil API key dari session_state yang diset di sidebar
        api_key = st.session_state.get("gemini_api_key", "")
        
        if not api_key:
            st.error("⚠️ Mohon masukkan Google Gemini API Key di menu sidebar terlebih dahulu.")
        elif not topik:
            st.warning("⚠️ Mohon isi topik pembelajaran.")
        else:
            with st.spinner("Sistem GEMA sedang menyusun Modul Ajar..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-3.5-flash")
                    
                    prompt = f"""
                    Buatlah Modul Ajar Kurikulum Merdeka yang komprehensif untuk:
                    Jenjang: {jenjang_pendidikan}, Mapel: {mata_pelajaran}, Fase: {fase_kelas}, 
                    Topik: {topik}, Waktu: {alokasi_waktu}.
                    Sekolah: {nama_sekolah}, Penyusun: {nama_penulis}.
                    """
                    
                    response = model.generate_content(prompt)
                    st.success("🎉 Modul Ajar GEMA Berhasil Disusun!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memanggil Gemini API: {e}")

# --- Sidebar untuk Mengatur API Key ---
with st.sidebar:
    st.header("⚙️ Pengaturan")
    api_key_input = st.text_input("Masukkan Google Gemini API Key", type="password")
    if api_key_input:
        st.session_state["gemini_api_key"] = api_key_input
        st.success("API Key tersimpan!")

# --- Pemanggilan Fungsi Utama ---
if __name__ == "__main__":
    render_gema()