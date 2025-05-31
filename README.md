# Sistem Pencarian Artikel DISPMD Buleleng

Aplikasi ini adalah sistem pencarian artikel yang mengambil data dari website DISPMD Buleleng dan menyediakan antarmuka pencarian berbasis Streamlit.

## Fitur

- Scraping artikel dari website DISPMD Buleleng
- Preprocessing teks Bahasa Indonesia
- Pencarian artikel menggunakan teknik TF-IDF
- Antarmuka web interaktif dengan Streamlit

## Persyaratan Sistem

- Python 3.x
- pip (Python package installer)

## Instalasi

1. Clone atau download repository ini

2. Install dependensi yang diperlukan:
```bash
pip install -r requirements.txt
```

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
- `indexer.py`: Modul untuk mengindeks dan mencari artikel
- `app.py`: Aplikasi Streamlit untuk antarmuka web
- `articles.json`: File penyimpanan artikel yang telah di-scrape
- `requirements.txt`: Daftar dependensi Python

## Cara Kerja Teknis

### 1. Scraping (scraper.py)
- Mengambil daftar artikel dari halaman berita DISPMD
- Mendukung paginasi dengan batasan halaman yang dapat dikonfigurasi
- Menyimpan artikel dalam format JSON dengan struktur: judul, URL, konten, dan tanggal
- Menghindari duplikasi artikel

### 2. Preprocessing (preprocess.py)
- Membersihkan teks dari karakter khusus
- Mengubah teks menjadi lowercase
- Menghapus stopwords Bahasa Indonesia
- Melakukan stemming untuk mendapatkan kata dasar

### 3. Indexing dan Pencarian (indexer.py)
- Menggunakan TF-IDF (Term Frequency-Inverse Document Frequency)
- Membangun matriks TF-IDF dari artikel yang telah dipreprocess
- Menghitung similarity antara query pencarian dan artikel

### 4. Antarmuka Web (app.py)
- Menyediakan input pencarian
- Menampilkan hasil pencarian berdasarkan relevance score
- Menampilkan detail artikel termasuk judul, tanggal, dan konten

## Pengembangan

Untuk menambahkan artikel baru:
1. Jalankan `scraper.py` untuk mengambil artikel terbaru
2. Artikel baru akan otomatis ditambahkan ke `articles.json`
3. Restart aplikasi Streamlit untuk memuat artikel baru

## Catatan

- Pastikan koneksi internet stabil saat melakukan scraping
- Waktu scraping tergantung pada jumlah artikel dan kecepatan internet
- Aplikasi akan membaca artikel dari `articles.json`, pastikan file tersebut ada dan valid
