# Sistem Pencarian Artikel DISPMD Buleleng

Aplikasi ini adalah sistem pencarian artikel yang mengambil data dari website DISPMD Buleleng dan menyediakan antarmuka pencarian berbasis Streamlit dengan dukungan algoritma pencarian ganda.

## Fitur

- **Scraping artikel** dari website DISPMD Buleleng dengan paginasi
- **Preprocessing teks** Bahasa Indonesia (cleaning, stemming, stopword removal)
- **Dual Search Algorithm**:
  - **TF-IDF** (Term Frequency-Inverse Document Frequency)
  - **BM25** (Best Matching 25) untuk hasil yang lebih akurat
- **Combined Scoring System** dengan bobot yang dapat disesuaikan
- **Antarmuka web interaktif** dengan Streamlit dan layout responsif
- **Model persistence** untuk performa yang optimal
- **Side-by-side comparison** hasil pencarian dari kedua algoritma

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

### 3. Dual Algorithm Indexing (indexer.py)

#### **TF-IDF (Term Frequency-Inverse Document Frequency)**
- Membangun matriks TF-IDF dari artikel yang telah dipreprocess
- Menghitung cosine similarity antara query dan dokumen
- Cocok untuk pencarian berbasis frekuensi kata

#### **BM25 (Best Matching 25)**
- Algoritma probabilistik yang lebih canggih dari TF-IDF
- Menangani dokumen dengan panjang yang bervariasi lebih baik
- Menggunakan parameter k1 dan b untuk fine-tuning
- Memberikan hasil yang lebih akurat untuk query pendek

#### **Combined Scoring System**
- Formula: `Combined Score = (α × Similarity Score) + ((1 - α) × Normalized Access Count)`
- α (alpha) dapat disesuaikan untuk menyeimbangkan relevansi vs popularitas
- Normalisasi access count ke skala [0,1] untuk keseimbangan

### 4. Antarmuka Web (app.py)
- **Dual search interface** dengan hasil TF-IDF dan BM25 side-by-side
- **Model management** dengan opsi load/create model
- **Interactive slider** untuk mengatur bobot α
- **Detailed metrics** untuk setiap artikel (similarity, access, combined score)
- **Responsive layout** dengan sidebar dan kolom terpisah
- **Error handling** dan loading indicators

## Pengembangan

Untuk menambahkan artikel baru:
1. Jalankan `scraper.py` untuk mengambil artikel terbaru
2. Artikel baru akan otomatis ditambahkan ke `articles.json`
3. Hapus `tfidf_model.pkl` atau gunakan opsi "Buat model baru" di UI untuk melatih ulang model
4. Restart aplikasi Streamlit untuk memuat artikel baru

## Metodologi dan Referensi Ilmiah

Sistem ini mengimplementasikan metodologi pencarian hybrid yang menggabungkan:

### **Algoritma Pencarian**
1. **TF-IDF**: Pendekatan klasik berbasis frekuensi term
2. **BM25**: Algoritma probabilistik modern dengan normalisasi panjang dokumen

### **Combined Scoring**
Menggunakan formula linear combination yang didasarkan pada penelitian:
- **Zhou et al. (2012)**: Hybrid approach untuk personalized search
- **Manning et al. (2008)**: Information retrieval fundamentals
- **Liu et al. (2011)**: Parameter sensitivity dalam learning to rank
- **Han et al. (2011)**: Data preprocessing dan normalisasi

### **Preprocessing Bahasa Indonesia**
- Menggunakan **Sastrawi** untuk stemming Bahasa Indonesia
- Stopword removal dengan daftar kata yang disesuaikan
- Text cleaning untuk menangani konten web

Detail lengkap rumus dan referensi dapat dilihat di `referensi_perhitungan.md`

## Catatan

- Pastikan koneksi internet stabil saat melakukan scraping
- Waktu scraping tergantung pada jumlah artikel dan kecepatan internet
- Model akan disimpan otomatis setelah training pertama untuk mempercepat loading
- Aplikasi akan membaca artikel dari `articles.json`, pastikan file tersebut ada dan valid
- Untuk performa optimal, gunakan model yang sudah ada kecuali ada artikel baru yang signifikan
