import json
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from preprocess import clean_text
import sys
import re
import numpy as np

# File untuk menyimpan model TF-IDF dan data terkait
MODEL_FILE = "tfidf_model.pkl"

def extract_access_count(tanggal):
    """Mengekstrak jumlah akses dari string tanggal.
    
    Args:
        tanggal (str): String tanggal yang berisi informasi jumlah akses
        
    Returns:
        int: Jumlah akses artikel, default 0 jika tidak ditemukan
    """
    try:
        # Mencari pola angka yang diikuti kata 'kali' di akhir string
        match = re.search(r'(\d+)\s*kali\s*$', tanggal)
        if match:
            return int(match.group(1))
        return 0
    except:
        return 0

# Variabel global untuk menyimpan data
articles = None
titles = None
access_counts = None
vectorizer = None
X = None
corpus = None
bm25 = None
tokenized_corpus = None

def initialize_model():
    """Inisialisasi model TF-IDF, BM25 dan data terkait.
    Jika file model sudah ada, muat dari file tersebut.
    Jika tidak, buat model baru dan simpan ke file.
    """
    global articles, titles, access_counts, vectorizer, X, corpus, bm25, tokenized_corpus
    
    try:
        # Cek apakah file model sudah ada
        if os.path.exists(MODEL_FILE):
            print("Memuat model TF-IDF dari file...", file=sys.stderr)
            try:
                # Muat model dari file
                with open(MODEL_FILE, 'rb') as f:
                    data = pickle.load(f)
                    articles = data['articles']
                    titles = data['titles']
                    access_counts = data['access_counts']
                    vectorizer = data['vectorizer']
                    X = data['X']
                    corpus = data['corpus']
                    bm25 = data.get('bm25', None)
                    tokenized_corpus = data.get('tokenized_corpus', None)
                
                print(f"Model berhasil dimuat. {len(articles)} artikel tersedia.", file=sys.stderr)
                print(f"Vocabulary size: {len(vectorizer.vocabulary_)}", file=sys.stderr)
                
                # Jika BM25 tidak ada dalam file lama, inisialisasi ulang
                if bm25 is None or tokenized_corpus is None:
                    print("Menginisialisasi BM25 untuk model lama...", file=sys.stderr)
                    tokenized_corpus = [doc.split() for doc in corpus]
                    bm25 = BM25Okapi(tokenized_corpus)
                    print(f"BM25 model initialized with {len(tokenized_corpus)} documents", file=sys.stderr)
                    # Simpan ulang model dengan BM25
                    save_model()
                
                return True
            except Exception as e:
                print(f"Error saat memuat model: {str(e)}. Membuat model baru...", file=sys.stderr)
        
        # Jika file tidak ada atau terjadi error saat memuat, buat model baru
        print("Membuat model TF-IDF baru...", file=sys.stderr)
        
        # Membaca data artikel dari file JSON
        with open("articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)

        # Print debugging information
        print(f"Number of articles loaded: {len(articles)}", file=sys.stderr)
        
        # Preprocessing konten artikel
        print("Original and cleaned texts for first few documents:", file=sys.stderr)
        for i, a in enumerate(articles[:3]):
            original_text = a['konten']
            cleaned_text = clean_text(original_text)
            print(f"Doc {i} original: {original_text[:100]}...", file=sys.stderr)
            print(f"Doc {i} cleaned: {cleaned_text[:100]}...", file=sys.stderr)

        corpus = [clean_text(a['konten']) for a in articles]
        # Print first few processed documents
        print("First few processed documents:", file=sys.stderr)
        for i, doc in enumerate(corpus[:3]):
            print(f"Doc {i}: {doc[:100]}...", file=sys.stderr)
        
        # Mengekstrak judul dan jumlah akses
        titles = [a['judul'] for a in articles]
        access_counts = [extract_access_count(a.get('tanggal', '0 kali')) for a in articles]
        
        # Menghitung skor TF-IDF
        vectorizer = TfidfVectorizer(min_df=1, stop_words=None)
        X = vectorizer.fit_transform(corpus)
        
        # Inisialisasi BM25
        print("Menginisialisasi BM25...", file=sys.stderr)
        tokenized_corpus = [doc.split() for doc in corpus]
        bm25 = BM25Okapi(tokenized_corpus)
        
        print(f"Vocabulary size: {len(vectorizer.vocabulary_)}", file=sys.stderr)
        print(f"Feature names: {list(vectorizer.vocabulary_.keys())[:10]}", file=sys.stderr)
        print(f"BM25 model initialized with {len(tokenized_corpus)} documents", file=sys.stderr)
        
        # Simpan model ke file
        save_model()
        
        return True
    except Exception as e:
        print(f"Error during initialization: {str(e)}", file=sys.stderr)
        raise

def save_model():
    """Menyimpan model TF-IDF, BM25 dan data terkait ke file."""
    try:
        print("Menyimpan model TF-IDF dan BM25 ke file...", file=sys.stderr)
        data = {
            'articles': articles,
            'titles': titles,
            'access_counts': access_counts,
            'vectorizer': vectorizer,
            'X': X,
            'corpus': corpus,
            'bm25': bm25,
            'tokenized_corpus': tokenized_corpus
        }
        with open(MODEL_FILE, 'wb') as f:
            pickle.dump(data, f)
        print(f"Model berhasil disimpan ke {MODEL_FILE}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Error saat menyimpan model: {str(e)}", file=sys.stderr)
        return False

def search_tfidf(query, alpha=0.7):
    """Mencari artikel menggunakan TF-IDF dengan mempertimbangkan similarity dan frekuensi akses.
    
    Args:
        query (str): Query pencarian
        alpha (float): Bobot untuk similarity score (1-alpha untuk skor frekuensi akses)
        
    Returns:
        list: Daftar artikel terurut berdasarkan kombinasi similarity dan frekuensi akses
    """
    cleaned_query = clean_text(query)
    
    # Menghitung similarity score
    query_vec = vectorizer.transform([cleaned_query])
    similarity = cosine_similarity(query_vec, X).flatten()
    
    # Normalisasi skor frekuensi akses
    max_access = max(access_counts) if access_counts else 1
    normalized_access = [count/max_access for count in access_counts]
    
    # Menghitung skor kombinasi
    combined_scores = [alpha * sim + (1-alpha) * acc 
                      for sim, acc in zip(similarity, normalized_access)]
    
    # Mendapatkan indeks artikel teratas
    top_indices = sorted(range(len(combined_scores)), 
                        key=lambda i: combined_scores[i], 
                        reverse=True)[:5]
    
    # Mengembalikan hasil pencarian dengan informasi lengkap
    results = [(titles[i], 
             articles[i]['url'], 
             similarity[i],
             access_counts[i],
             combined_scores[i]) for i in top_indices]
    
    return results

def search_bm25(query, alpha=0.7):
    """Mencari artikel menggunakan BM25 dengan mempertimbangkan similarity dan frekuensi akses.
    
    Args:
        query (str): Query pencarian
        alpha (float): Bobot untuk BM25 score (1-alpha untuk skor frekuensi akses)
        
    Returns:
        list: Daftar artikel terurut berdasarkan kombinasi BM25 score dan frekuensi akses
    """
    cleaned_query = clean_text(query)
    tokenized_query = cleaned_query.split()
    
    # Menghitung BM25 scores
    bm25_scores = bm25.get_scores(tokenized_query)
    
    # Normalisasi skor frekuensi akses
    max_access = max(access_counts) if access_counts else 1
    normalized_access = [count/max_access for count in access_counts]
    
    # Normalisasi BM25 scores
    max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
    normalized_bm25 = [score/max_bm25 for score in bm25_scores]
    
    # Menghitung skor kombinasi
    combined_scores = [alpha * bm25_score + (1-alpha) * acc 
                      for bm25_score, acc in zip(normalized_bm25, normalized_access)]
    
    # Mendapatkan indeks artikel teratas
    top_indices = sorted(range(len(combined_scores)), 
                        key=lambda i: combined_scores[i], 
                        reverse=True)[:5]
    
    # Mengembalikan hasil pencarian dengan informasi lengkap
    results = [(titles[i], 
             articles[i]['url'], 
             bm25_scores[i],
             access_counts[i],
             combined_scores[i]) for i in top_indices]
    
    return results

def search(query, alpha=0.7):
    """Mencari artikel menggunakan kedua metode: TF-IDF dan BM25.
    
    Args:
        query (str): Query pencarian
        alpha (float): Bobot untuk similarity/BM25 score (1-alpha untuk skor frekuensi akses)
    """
    print(f"\nMencari dengan query: '{query}'")
    print(f"Preprocessing query...")
    cleaned_query = clean_text(query)
    print(f"Query setelah preprocessing: '{cleaned_query}'\n")
    
    # Pencarian dengan TF-IDF
    print("\n" + "="*60)
    print("HASIL PENCARIAN MENGGUNAKAN TF-IDF")
    print("="*60)
    
    tfidf_results = search_tfidf(query, alpha)
    if not tfidf_results:
        print("Tidak ditemukan hasil yang sesuai dengan TF-IDF.")
    else:
        for i, (title, url, sim, acc, score) in enumerate(tfidf_results, 1):
            print(f"\nHasil #{i}")
            print(f"Judul: {title}")
            print(f"URL: {url}")
            print(f"TF-IDF Similarity Score: {sim:.4f}")
            print(f"Access Count: {acc}")
            print(f"Combined Score: {score:.4f}")
            print("-" * 50)
    
    # Pencarian dengan BM25
    print("\n" + "="*60)
    print("HASIL PENCARIAN MENGGUNAKAN BM25")
    print("="*60)
    
    bm25_results = search_bm25(query, alpha)
    if not bm25_results:
        print("Tidak ditemukan hasil yang sesuai dengan BM25.")
    else:
        for i, (title, url, bm25_score, acc, score) in enumerate(bm25_results, 1):
            print(f"\nHasil #{i}")
            print(f"Judul: {title}")
            print(f"URL: {url}")
            print(f"BM25 Score: {bm25_score:.4f}")
            print(f"Access Count: {acc}")
            print(f"Combined Score: {score:.4f}")
            print("-" * 50)
    
    return tfidf_results, bm25_results


if __name__ == "__main__":
    try:
        print("\n===== SISTEM TEMU BALIK INFORMASI =====\n")
        
        # Inisialisasi model
        if os.path.exists(MODEL_FILE):
            print("\n1. Gunakan model yang sudah ada")
            print("2. Buat model baru (proses ulang data)")
            model_choice = input("Pilih opsi model (1/2): ")
            
            if model_choice == "2":
                # Hapus file model lama jika ada
                if os.path.exists(MODEL_FILE):
                    os.remove(MODEL_FILE)
                    print(f"File model lama {MODEL_FILE} dihapus.")
        
        # Inisialisasi model (akan memuat dari file jika ada, atau membuat baru jika tidak ada)
        initialize_model()
        
        # Menu pencarian
        while True:
            print("\n===== MENU PENCARIAN =====\n")
            print("1. Gunakan query hardcoded")
            print("2. Masukkan query secara manual")
            print("3. Keluar")
            choice = input("Pilih opsi (1/2/3): ")
            
            if choice == "3":
                print("Terima kasih telah menggunakan sistem pencarian!")
                break
            
            if choice == "1":
                # Opsi 1: Hardcoded query
                query = "ekonomi desa"
                print(f"\nMenggunakan query hardcoded: '{query}'")
            else:
                # Opsi 2: Input dari user
                query = input("\nMasukkan query pencarian: ")
            
            # Jalankan pencarian
            search(query)
            
    except Exception as e:
        print(f"Error during search: {str(e)}", file=sys.stderr)
