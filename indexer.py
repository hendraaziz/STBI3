import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import clean_text
import sys

try:
    with open("articles.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    # Print debugging information
    print(f"Number of articles loaded: {len(articles)}", file=sys.stderr)
    
    corpus = [clean_text(a['konten']) for a in articles]
    # Print first few processed documents
    print("First few processed documents:", file=sys.stderr)
    for i, doc in enumerate(corpus[:3]):
        print(f"Doc {i}: {doc[:100]}...", file=sys.stderr)
    
    titles = [a['judul'] for a in articles]

    vectorizer = TfidfVectorizer(min_df=1, stop_words=None)
    X = vectorizer.fit_transform(corpus)
    
    print(f"Vocabulary size: {len(vectorizer.vocabulary_)}", file=sys.stderr)
    print(f"Feature names: {list(vectorizer.vocabulary_.keys())[:10]}", file=sys.stderr)

except Exception as e:
    print(f"Error during initialization: {str(e)}", file=sys.stderr)
    raise

def search(query):
    query_vec = vectorizer.transform([clean_text(query)])
    similarity = cosine_similarity(query_vec, X).flatten()
    top_indices = similarity.argsort()[::-1][:5]
    return [(titles[i], articles[i]['url'], similarity[i]) for i in top_indices]
