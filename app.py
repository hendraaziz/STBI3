import streamlit as st
from indexer import search

st.title("Sistem Pencarian Artikel DISPMD Buleleng")

query = st.text_input("Masukkan kata kunci:")

if query:
    results = search(query)
    for judul, url, score in results:
        st.markdown(f"### [{judul}]({url})\nSkor relevansi: `{score:.2f}`")
