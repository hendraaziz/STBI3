import streamlit as st
from indexer import search

st.title("Sistem Pencarian Artikel DISPMD Buleleng")

# Menambahkan slider untuk mengatur bobot similarity score
alpha = st.slider(
    "Bobot Relevansi Konten",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    help="Semakin tinggi nilai, semakin besar pengaruh kemiripan konten. Semakin rendah, semakin besar pengaruh popularitas artikel."
)

# Input query pencarian
query = st.text_input("Masukkan kata kunci:")

if query:
    # Melakukan pencarian dengan parameter alpha
    results = search(query, alpha)
    
    # Menampilkan hasil pencarian
    for judul, url, sim_score, access_count, combined_score in results:
        st.markdown(f"### [{judul}]({url})")
        
        # Membuat kolom untuk menampilkan metrik
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Relevansi Konten",
                f"{sim_score:.2f}",
                help="Skor kemiripan konten artikel dengan kata kunci pencarian"
            )
        
        with col2:
            st.metric(
                "Jumlah Akses",
                f"{access_count} kali",
                help="Frekuensi artikel diakses oleh pengguna"
            )
        
        with col3:
            st.metric(
                "Skor Akhir",
                f"{combined_score:.2f}",
                help="Skor kombinasi dari relevansi konten dan popularitas artikel"
            )
        
        st.divider()  # Menambahkan garis pemisah antar artikel
