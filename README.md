# Sistem Pencarian Artikel DISPMD Buleleng

Aplikasi ini adalah sistem pencarian artikel yang mengambil data dari website DISPMD Buleleng dan menyediakan antarmuka pencarian berbasis Streamlit dengan dukungan algoritma pencarian ganda.

## Fitur

- **Scraping artikel** dari website DISPMD Buleleng dengan paginasi
- **Preprocessing teks** Bahasa Indonesia (cleaning, stemming, stopword removal)
- **Triple Search Algorithm**:
  - **TF-IDF** (Term Frequency-Inverse Document Frequency)
  - **BM25** (Best Matching 25) untuk hasil yang lebih akurat
  - **AI Expert (ChatGPT)** untuk analisis semantik mendalam
- **Combined Scoring System** dengan bobot yang dapat disesuaikan
- **Antarmuka web interaktif** dengan Streamlit dan layout responsif
- **Model persistence** untuk performa yang optimal
- **Multi-algorithm comparison** hasil pencarian dari tiga algoritma

## 🚀 Demo Live

Aplikasi ini telah di-deploy dan dapat diakses secara langsung di:
**[https://huggingface.co/spaces/frday/search_artikel](https://huggingface.co/spaces/frday/search_artikel)**

*Catatan: Demo mungkin dalam status "sleeping" karena inaktivitas. Klik link untuk mengaktifkan kembali.*

## Persyaratan Sistem

- Python 3.8 atau lebih baru
- pip (Python package installer)
- Koneksi internet untuk scraping artikel

## Instalasi

1. Clone atau download repository ini

2. Install dependensi yang diperlukan:
```bash
pip install -r requirements.txt
```

**Dependensi utama:**
- `streamlit` - Framework web untuk antarmuka
- `scikit-learn` - Library machine learning untuk TF-IDF
- `rank-bm25` - Implementasi algoritma BM25
- `openai` - API ChatGPT untuk AI Expert analysis
- `beautifulsoup4` - Web scraping
- `requests` - HTTP requests
- `Sastrawi` - Stemming Bahasa Indonesia

## Cara Penggunaan

### 1. Mengambil Artikel

Untuk mengambil artikel dari website DISPMD Buleleng:

```bash
python scraper.py
```

Parameter yang dapat diatur:
- Jumlah halaman maksimum yang akan di-scrape dapat diatur di `scraper.py` (default: 10 halaman)
- Untuk scraping tanpa batas halaman, set `max_pages = 0`

### 2. Menjalankan Aplikasi Pencarian

Untuk menjalankan antarmuka web pencarian:

```bash
streamlit run app.py
```

Aplikasi akan dapat diakses melalui browser di:
- Local URL: http://localhost:8501
- Network URL: http://[your-ip]:8501

## Struktur Aplikasi

- `scraper.py`: Script untuk mengambil artikel dari website DISPMD
- `preprocess.py`: Modul preprocessing teks Bahasa Indonesia
- `indexer.py`: Modul untuk mengindeks dan mencari artikel (TF-IDF & BM25)
- `app.py`: Aplikasi Streamlit untuk antarmuka web dengan dual algorithm
- `articles.json`: File penyimpanan artikel yang telah di-scrape
- `tfidf_model.pkl`: Model TF-IDF dan BM25 yang telah dilatih
- `requirements.txt`: Daftar dependensi Python
- `referensi_perhitungan.md`: Dokumentasi rumus dan referensi ilmiah

## Cara Kerja Teknis

### 1. Scraping (scraper.py)
- Mengambil daftar artikel dari halaman berita DISPMD
- Mendukung paginasi dengan batasan halaman yang dapat dikonfigurasi
- Menyimpan artikel dalam format JSON dengan struktur: judul, URL, konten, tanggal, dan access_count
- Menghindari duplikasi artikel

### 2. Preprocessing (preprocess.py)
- Membersihkan teks dari karakter khusus dan HTML tags
- Mengubah teks menjadi lowercase
- Menghapus stopwords Bahasa Indonesia
- Melakukan stemming untuk mendapatkan kata dasar menggunakan Sastrawi

### 3. Triple Algorithm Indexing (indexer.py)

#### **TF-IDF (Term Frequency-Inverse Document Frequency)**
- Membangun matriks TF-IDF dari artikel yang telah dipreprocess
- Menghitung cosine similarity antara query dan dokumen
- Cocok untuk pencarian berbasis frekuensi kata

#### **BM25 (Best Matching 25)**
- Algoritma probabilistik yang lebih canggih dari TF-IDF
- Menangani dokumen dengan panjang yang bervariasi lebih baik
- Menggunakan parameter k1 dan b untuk fine-tuning
- Memberikan hasil yang lebih akurat untuk query pendek

#### **AI Expert (ChatGPT)**
- Menggunakan ChatGPT-3.5-turbo untuk analisis semantik mendalam
- Menilai relevansi artikel berdasarkan pemahaman konteks dan makna
- Memberikan reasoning/penjelasan untuk setiap penilaian
- Mempertimbangkan konteks pemerintahan daerah Buleleng

#### **Combined Scoring System**
- Formula: `Combined Score = (α × Similarity Score) + ((1 - α) × Normalized Access Count)`
- α (alpha) dapat disesuaikan untuk menyeimbangkan relevansi vs popularitas
- Normalisasi access count ke skala [0,1] untuk keseimbangan

### 4. Antarmuka Web (app.py)
- **Triple search interface** dengan hasil TF-IDF, BM25, dan AI Expert side-by-side
- **Model management** dengan opsi load/create model
- **Interactive slider** untuk mengatur bobot α
- **AI Expert integration** dengan ChatGPT untuk analisis semantik
- **Detailed metrics** untuk setiap artikel (similarity, access, combined score, AI reasoning)
- **Responsive layout** dengan sidebar dan kolom terpisah untuk multi-algoritma
- **Error handling** dan loading indicators

## Pengembangan

Untuk menambahkan artikel baru:
1. Jalankan `scraper.py` untuk mengambil artikel terbaru
2. Artikel baru akan otomatis ditambahkan ke `articles.json`
3. Hapus `tfidf_model.pkl` atau gunakan opsi "Buat model baru" di UI untuk melatih ulang model
4. Restart aplikasi Streamlit untuk memuat artikel baru

## 📚 Metodologi dan Referensi Ilmiah

### **Hybrid Search Methodology**
Sistem ini mengimplementasikan pendekatan hybrid yang menggabungkan:
- **TF-IDF**: Algoritma klasik berbasis statistik untuk analisis frekuensi kata
- **BM25**: Algoritma probabilistik modern yang lebih efektif untuk dokumen dengan panjang bervariasi
- **AI Expert**: Analisis semantik menggunakan Large Language Model (ChatGPT) untuk pemahaman konteks mendalam

### **AI Expert Integration**
Fitur AI Expert menggunakan:
- **ChatGPT-3.5-turbo** untuk analisis semantik
- **Context-aware evaluation** dengan pemahaman domain pemerintahan daerah
- **Reasoning explanation** untuk transparansi penilaian
- **Semantic similarity** yang melampaui keyword matching

### **Combined Scoring berdasarkan Penelitian**
Formula combined scoring didasarkan pada penelitian tentang personalized search dan learning to rank, dengan mempertimbangkan:
- Relevansi konten (similarity score dari TF-IDF/BM25/AI)
- Popularitas artikel (normalized access count)
- Bobot yang dapat disesuaikan (parameter α)

### **Indonesian Text Preprocessing**
Menggunakan library Sastrawi untuk:
- Stemming Bahasa Indonesia
- Stopword removal
- Text normalization

### **Referensi Lengkap**
Lihat file `referensi_perhitungan.md` untuk detail metodologi dan referensi ilmiah yang digunakan.

## Catatan

- Pastikan koneksi internet stabil saat melakukan scraping
- Waktu scraping tergantung pada jumlah artikel dan kecepatan internet
- Model akan disimpan otomatis setelah training pertama untuk mempercepat loading
- Aplikasi akan membaca artikel dari `articles.json`, pastikan file tersebut ada dan valid
- Untuk performa optimal, gunakan model yang sudah ada kecuali ada artikel baru yang signifikan
