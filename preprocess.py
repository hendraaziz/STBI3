import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

factory = StemmerFactory()
stemmer = factory.create_stemmer()

# Stopword list (bisa diperluas sesuai kebutuhan)
stopwords = set([
    'yang', 'untuk', 'dengan', 'dari', 'dan', 'di', 'ke', 'pada', 'adalah',
    'itu', 'ini', 'kami', 'kita', 'mereka', 'saya', 'anda', 'atau', 'sebagai',
    'juga', 'dalam', 'akan', 'telah', 'tidak', 'bagi', 'oleh', 'karena'
])

def clean_text(text):
    print("Starting to clean text...")
    # Convert to lowercase
    text = text.lower()
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Apply stemming if text is not empty
    if text:
        cleaned = stemmer.stem(text)
        
        # Tokenization (split into words)
        tokens = cleaned.split()
        
        # Stopword removal
        tokens = [word for word in tokens if word not in stopwords]
        
        # Join tokens back into text
        result = ' '.join(tokens)
        
        print("Finished cleaning text.")
        return result
    print("No text to clean.")
    return text
