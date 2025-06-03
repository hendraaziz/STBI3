import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import clean_text
import sys
import re

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

try:
    # Membaca data artikel dari file JSON
    with open("articles.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    # Print debugging information
    print(f"Number of articles loaded: {len(articles)}", file=sys.stderr)
    
    # Preprocessing konten artikel
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

except Exception as e:
    print(f"Error during initialization: {str(e)}", file=sys.stderr)
    raise

def search(query, alpha=0.7):
    """Mencari artikel berdasarkan query dengan mempertimbangkan similarity dan frekuensi akses.
    
    Args:
        query (str): Query pencarian
        alpha (float): Bobot untuk similarity score (1-alpha untuk skor frekuensi akses)
        
    Returns:
        list: Daftar artikel terurut berdasarkan kombinasi similarity dan frekuensi akses
    """
    # Menghitung similarity score
    query_vec = vectorizer.transform([clean_text(query)])
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
    return [(titles[i], 
             articles[i]['url'], 
             similarity[i],
             access_counts[i],
             combined_scores[i]) for i in top_indices]
