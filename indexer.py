import json
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import clean_text
import sys
import re

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

def initialize_model():
    """Inisialisasi model TF-IDF dan data terkait.
    Jika file model sudah ada, muat dari file tersebut.
    Jika tidak, buat model baru dan simpan ke file.
    """
    global articles, titles, access_counts, vectorizer, X, corpus
    
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
                
                print(f"Model berhasil dimuat. {len(articles)} artikel tersedia.", file=sys.stderr)
                print(f"Vocabulary size: {len(vectorizer.vocabulary_)}", file=sys.stderr)
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
        
        print(f"Vocabulary size: {len(vectorizer.vocabulary_)}", file=sys.stderr)
        print(f"Feature names: {list(vectorizer.vocabulary_.keys())[:10]}", file=sys.stderr)
        
        # Simpan model ke file
        save_model()
        
        return True
    except Exception as e:
        print(f"Error during initialization: {str(e)}", file=sys.stderr)
        raise

def save_model():
    """Menyimpan model TF-IDF dan data terkait ke file."""
    try:
        print("Menyimpan model TF-IDF ke file...", file=sys.stderr)
        data = {
            'articles': articles,
            'titles': titles,
            'access_counts': access_counts,
            'vectorizer': vectorizer,
            'X': X,
            'corpus': corpus
        }
        with open(MODEL_FILE, 'wb') as f:
            pickle.dump(data, f)
        print(f"Model berhasil disimpan ke {MODEL_FILE}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Error saat menyimpan model: {str(e)}", file=sys.stderr)
        return False

def search(query, alpha=0.7):
    """Mencari artikel berdasarkan query dengan mempertimbangkan similarity dan frekuensi akses.
    
    Args:
        query (str): Query pencarian
        alpha (float): Bobot untuk similarity score (1-alpha untuk skor frekuensi akses)
        
    Returns:
        list: Daftar artikel terurut berdasarkan kombinasi similarity dan frekuensi akses
    """
    print(f"\nMencari dengan query: '{query}'")
    print(f"Preprocessing query...")
    cleaned_query = clean_text(query)
    print(f"Query setelah preprocessing: '{cleaned_query}'\n")
    
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
    
    # Menampilkan hasil pencarian di terminal
    print("\n===== HASIL PENCARIAN =====\n")
    if not results:
        print("Tidak ditemukan hasil yang sesuai.")
    else:
        for i, (title, url, sim, acc, score) in enumerate(results, 1):
            print(f"Hasil #{i}")
            print(f"Judul: {title}")
            print(f"URL: {url}")
            print(f"Similarity Score: {sim:.4f}")
            print(f"Access Count: {acc}")
            print(f"Combined Score: {score:.4f}")
            print("-" * 50)
    
    return results


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
