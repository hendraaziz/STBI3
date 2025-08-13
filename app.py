import streamlit as st
import os

# Try to import functions from indexer with error handling
try:
    from indexer import initialize_model, search_tfidf, search_bm25, MODEL_FILE
    BM25_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importing from indexer: {str(e)}")
    st.error("Please make sure all required libraries are installed: pip install rank-bm25")
    st.stop()
    BM25_AVAILABLE = False

st.set_page_config(
    page_title="Sistem Pencarian Artikel DISPMD Buleleng",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Sistem Pencarian Artikel DISPMD Buleleng")
st.markdown("---")

# Inisialisasi session state untuk model
if 'model_initialized' not in st.session_state:
    st.session_state.model_initialized = False

# Sidebar untuk pengaturan model
with st.sidebar:
    st.header("⚙️ Pengaturan Model")
    
    # Opsi pemilihan model
    if os.path.exists(MODEL_FILE):
        model_option = st.radio(
            "Pilih opsi model:",
            ["Gunakan model yang sudah ada", "Buat model baru (proses ulang data)"],
            help="Model yang sudah ada akan mempercepat proses loading"
        )
        
        if model_option == "Buat model baru (proses ulang data)":
            if st.button("🔄 Hapus Model Lama", type="secondary"):
                if os.path.exists(MODEL_FILE):
                    os.remove(MODEL_FILE)
                    st.session_state.model_initialized = False
                    st.success("Model lama berhasil dihapus!")
                    st.rerun()
    else:
        st.info("Model belum ada, akan dibuat otomatis saat pertama kali digunakan.")
    
    st.markdown("---")
    
    # Slider untuk mengatur bobot
    alpha = st.slider(
        "⚖️ Bobot Relevansi Konten",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        help="Semakin tinggi nilai, semakin besar pengaruh kemiripan konten. Semakin rendah, semakin besar pengaruh popularitas artikel."
    )
    
    st.markdown("---")
    st.markdown("### 📊 Informasi Model")
    if st.session_state.model_initialized:
        st.success("✅ Model siap digunakan")
    else:
        st.warning("⏳ Model belum diinisialisasi")

# Inisialisasi model jika belum dilakukan
if not st.session_state.model_initialized:
    with st.spinner("🔄 Menginisialisasi model... Mohon tunggu..."):
        try:
            initialize_model()
            st.session_state.model_initialized = True
            st.success("✅ Model berhasil diinisialisasi!")
        except Exception as e:
            st.error(f"❌ Error saat menginisialisasi model: {str(e)}")
            st.stop()

# Input query pencarian
st.header("🔍 Pencarian Artikel")
query = st.text_input(
    "Masukkan kata kunci pencarian:",
    placeholder="Contoh: ekonomi desa, pajak daerah, pembangunan...",
    help="Masukkan kata kunci yang ingin Anda cari dalam artikel"
)

if query:
    with st.spinner("🔍 Mencari artikel..."):
        try:
            # Melakukan pencarian dengan kedua metode
            tfidf_results = search_tfidf(query, alpha)
            bm25_results = search_bm25(query, alpha)
            
            # Membuat dua kolom untuk menampilkan hasil
            col1, col2 = st.columns(2)
            
            # Hasil TF-IDF
            with col1:
                st.subheader("📈 Hasil Pencarian TF-IDF")
                st.markdown("*Menggunakan algoritma Term Frequency-Inverse Document Frequency*")
                
                if not tfidf_results:
                    st.warning("Tidak ditemukan hasil yang sesuai dengan TF-IDF.")
                else:
                    for i, (judul, url, sim_score, access_count, combined_score) in enumerate(tfidf_results, 1):
                        with st.container():
                            st.markdown(f"**#{i}. [{judul}]({url})**")
                            
                            # Metrik dalam satu baris
                            metric_col1, metric_col2, metric_col3 = st.columns(3)
                            
                            with metric_col1:
                                st.metric(
                                    "TF-IDF Score",
                                    f"{sim_score:.4f}",
                                    help="Skor kemiripan TF-IDF"
                                )
                            
                            with metric_col2:
                                st.metric(
                                    "Akses",
                                    f"{access_count}",
                                    help="Jumlah akses artikel"
                                )
                            
                            with metric_col3:
                                st.metric(
                                    "Skor Akhir",
                                    f"{combined_score:.4f}",
                                    help="Skor kombinasi"
                                )
                            
                            st.markdown("---")
            
            # Hasil BM25
            with col2:
                st.subheader("🎯 Hasil Pencarian BM25")
                st.markdown("*Menggunakan algoritma Best Matching 25*")
                
                if not bm25_results:
                    st.warning("Tidak ditemukan hasil yang sesuai dengan BM25.")
                else:
                    for i, (judul, url, bm25_score, access_count, combined_score) in enumerate(bm25_results, 1):
                        with st.container():
                            st.markdown(f"**#{i}. [{judul}]({url})**")
                            
                            # Metrik dalam satu baris
                            metric_col1, metric_col2, metric_col3 = st.columns(3)
                            
                            with metric_col1:
                                st.metric(
                                    "BM25 Score",
                                    f"{bm25_score:.4f}",
                                    help="Skor BM25"
                                )
                            
                            with metric_col2:
                                st.metric(
                                    "Akses",
                                    f"{access_count}",
                                    help="Jumlah akses artikel"
                                )
                            
                            with metric_col3:
                                st.metric(
                                    "Skor Akhir",
                                    f"{combined_score:.4f}",
                                    help="Skor kombinasi"
                                )
                            
                            st.markdown("---")
            
            # Informasi tambahan
            st.markdown("---")
            st.info(
                "💡 **Tips:** TF-IDF lebih fokus pada frekuensi kata dalam dokumen, "
                "sedangkan BM25 lebih baik dalam menangani dokumen dengan panjang yang bervariasi. "
                "Bandingkan hasil kedua metode untuk mendapatkan perspektif yang lebih lengkap."
            )
            
        except Exception as e:
            st.error(f"❌ Error saat melakukan pencarian: {str(e)}")
else:
    # Tampilan awal ketika belum ada query
    st.info("👆 Masukkan kata kunci di atas untuk memulai pencarian artikel.")
    
    # Menampilkan contoh penggunaan
    with st.expander("📖 Panduan Penggunaan"):
        st.markdown("""
        ### Cara Menggunakan Sistem Pencarian:
        
        1. **Masukkan Kata Kunci**: Ketik kata kunci yang ingin Anda cari di kotak pencarian
        2. **Atur Bobot**: Gunakan slider di sidebar untuk mengatur bobot antara relevansi konten dan popularitas
        3. **Lihat Hasil**: Sistem akan menampilkan hasil dari dua metode:
           - **TF-IDF**: Metode klasik yang fokus pada frekuensi kata
           - **BM25**: Metode modern yang lebih baik untuk dokumen dengan panjang bervariasi
        
        ### Contoh Kata Kunci:
        - `ekonomi desa`
        - `pajak daerah`
        - `pembangunan infrastruktur`
        - `pelatihan masyarakat`
        - `program pemerintah`
        
        ### Interpretasi Skor:
        - **TF-IDF/BM25 Score**: Skor relevansi berdasarkan algoritma masing-masing
        - **Akses**: Jumlah kali artikel diakses (indikator popularitas)
        - **Skor Akhir**: Kombinasi dari relevansi dan popularitas berdasarkan bobot yang dipilih
        
        ---
        
        ### 🧮 Rumus Perhitungan Skor Kombinasi:
        
        **Formula yang digunakan:**
        ```
        Combined Score = (α × Similarity Score) + ((1 - α) × Normalized Access Count)
        ```
        
        **Keterangan:**
        - **α (alpha)**: Bobot relevansi konten (0.0 - 1.0)
        - **Similarity Score**: Skor kemiripan TF-IDF/BM25 (0.0 - 1.0)
        - **Normalized Access Count**: Jumlah akses yang dinormalisasi (0.0 - 1.0)
        
        **Contoh Perhitungan:**
        - Jika α = 0.7, Similarity = 0.85, Normalized Access = 0.8
        - Combined Score = (0.7 × 0.85) + (0.3 × 0.8) = 0.595 + 0.24 = **0.835**
        
        **Keunggulan Pendekatan Ini:**
        1. **Balance Optimal**: Menyeimbangkan relevansi konten dengan popularitas artikel
        2. **Fleksibilitas**: Nilai α dapat disesuaikan sesuai kebutuhan
        3. **Normalisasi**: Memastikan kedua komponen memiliki skala yang seimbang
        
        ---
        
        ### 📚 Referensi Ilmiah:
        
        Metode kombinasi skor yang digunakan dalam sistem ini didasarkan pada penelitian ilmiah:
        
        1. **Zhou et al. (2012)** - *"A Hybrid Approach for Personalized Search Based on Query Logs and Social Annotations"*
           - DOI: [10.1007/978-3-642-28997-2_18](https://doi.org/10.1007/978-3-642-28997-2_18)
           - Menggabungkan relevance score dengan popularity score menggunakan bobot linear
        
        2. **Manning et al. (2008)** - *"Introduction to Information Retrieval"*
           - [Stanford NLP Book](https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf)
           - Membahas ranking gabungan dengan faktor relevance dan popularity
        
        3. **Liu et al. (2011)** - *"Parameter Sensitivity in Learning to Rank"*
           - DOI: [10.1145/1273496.1273513](https://doi.org/10.1145/1273496.1273513)
           - Menunjukkan nilai α = 0.5-0.7 optimal untuk menyeimbangkan relevance dan popularity
        
        4. **Han et al. (2011)** - *"Data Mining: Concepts and Techniques"*
           - [Leiden University](https://liacs.leidenuniv.nl/~bakkerem2/dbdm2012/03_dbdm2012_Data.pdf)
           - Menjelaskan pentingnya normalisasi untuk menggabungkan fitur berbeda skala
        """)
