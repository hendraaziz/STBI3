import requests
from bs4 import BeautifulSoup
import json
import time

import logging

# Konfigurasi logging
logging.basicConfig(
    level=logging.DEBUG,  # Ubah ke DEBUG untuk informasi lebih detail
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BASE_URL = "https://dispmd.bulelengkab.go.id"

def scrape_article_list(max_pages=3):
    all_urls = []
    max_retries = 3
    page = 1
    
    # max_pages = 0 berarti tidak ada batasan halaman
    if max_pages < 0:
        logging.warning("max_pages tidak boleh negatif, menggunakan nilai default 0 (unlimited)")
        max_pages = 0
    
    while True:
        # Cek batasan halaman jika max_pages > 0
        if max_pages > 0 and page > max_pages:
            logging.info(f"Mencapai batas maksimum halaman ({max_pages})")
            break
            
        try:
            # Akses halaman dengan nomor halaman
            page_url = f"{BASE_URL}/informasi/tampil/berita?page_v_konten={page}"
            logging.info(f"Mengambil daftar artikel dari halaman {page}: {page_url}")
            
            response = requests.get(page_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            logging.debug(f"HTML Response untuk halaman {page}:\n{soup.prettify()[:1000]}...")
            
            # Cek apakah halaman menampilkan "BELUM ADA DATA"
            no_data_text = soup.find(string=lambda text: "BELUM ADA DATA" in str(text) if text else False)
            if no_data_text:
                logging.info(f"Mencapai akhir data pada halaman {page}")
                break
            
            # Coba beberapa selector untuk menemukan artikel
            article_links = []
            selectors = [
                'div.berita a',  # Original selector
                'div.artikel a',  # Alternative selector
                'a[href*="/informasi/detail/berita"]',  # Direct link selector
                '.content-berita a'  # Content area selector
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    article_links.extend(links)
                    logging.debug(f"Menemukan {len(links)} link dengan selector '{selector}'")
            
            found_articles = False
            for link in article_links:
                if link.get('href') and '/informasi/detail/berita' in link['href']:
                    article_url = BASE_URL + link['href'] if link['href'].startswith('/') else link['href']
                    if article_url not in all_urls:
                        all_urls.append(article_url)
                        logging.info(f"Menemukan artikel baru: {link.text.strip() or 'Tanpa judul'}")
                        found_articles = True
            
            if found_articles:
                page += 1  # Lanjut ke halaman berikutnya
                logging.info(f"Berhasil mengambil artikel dari halaman {page-1}, melanjutkan ke halaman berikutnya")
            else:
                logging.warning(f"Tidak menemukan link artikel pada halaman {page}")
                # Periksa apakah ini karena format halaman yang berbeda
                logging.debug("Struktur HTML halaman:")
                logging.debug(soup.select('div.berita'))
                break
            
            # Tunggu sebentar sebelum mengambil halaman berikutnya
            time.sleep(2)
            
        except requests.RequestException as e:
            logging.error(f"Gagal mengambil halaman {page}: {str(e)}")
            if page == 1:  # Jika gagal pada halaman pertama, return langsung
                return all_urls
            break  # Jika gagal pada halaman selanjutnya, hentikan paginasi
        except Exception as e:
            logging.error(f"Error tidak terduga pada halaman {page}: {str(e)}")
            logging.debug(f"Traceback:", exc_info=True)
            break
    
    logging.info(f"Total artikel yang ditemukan: {len(all_urls)}")
    return all_urls

def scrape_article_detail(url):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logging.info(f"Mengambil artikel dari {url} (Percobaan {attempt + 1})")
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, 'html.parser')
            logging.debug(f"HTML Response untuk artikel:\n{soup.prettify()[:1000]}...")
            
            # Coba beberapa selector untuk judul
            title_selectors = [
                'h3.judul-konten',
                '.judul-konten',
                'div.col-md-8 h3',
                'h3',
                '.content-berita h3'
            ]
            title_elem = None
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    logging.debug(f"Judul ditemukan dengan selector: {selector}")
                    break
            
            if not title_elem:
                logging.error("Judul tidak ditemukan dengan semua selector yang dicoba")
                raise ValueError("Judul artikel tidak ditemukan")
            
            title = title_elem.text.strip()
            logging.debug(f"Judul artikel: {title}")
            
            # Coba beberapa selector untuk konten
            content_selectors = [
                'div.isi-konten p',
                '.konten p',
                'div.col-md-8 p',
                '.content-berita p',
                'article p',
                '.berita p'
            ]
            content = ""
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    logging.debug(f"Konten ditemukan dengan selector: {selector} ({len(paragraphs)} paragraf)")
                    content = " ".join([p.text.strip() for p in paragraphs])
                    break
            
            if not content:
                logging.error("Konten tidak ditemukan dengan semua selector yang dicoba")
                logging.debug("Mencoba mencari semua paragraf dalam dokumen...")
                all_paragraphs = soup.find_all('p')
                if all_paragraphs:
                    content = " ".join([p.text.strip() for p in all_paragraphs])
                    logging.debug(f"Menemukan {len(all_paragraphs)} paragraf dengan pencarian umum")
                else:
                    raise ValueError("Konten artikel tidak ditemukan")
            
            # Coba beberapa selector untuk tanggal
            date_selectors = [
                'div.text-muted',
                '.tanggal',
                '.date-info',
                '.content-berita .text-muted',
                'time'
            ]
            date_elem = None
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    logging.debug(f"Tanggal ditemukan dengan selector: {selector}")
                    break
            
            date_info = date_elem.text.strip() if date_elem else "Tanggal tidak tersedia"
            logging.debug(f"Informasi tanggal: {date_info}")
            
            logging.info(f"Berhasil mengambil artikel: {title}")
            return {
                "judul": title,
                "url": url,
                "konten": content,
                "tanggal": date_info
            }
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Gagal mengambil artikel dari {url} setelah {max_retries} percobaan: {str(e)}")
                raise
            print(f"Percobaan {attempt + 1} gagal, mencoba lagi...")
            time.sleep(2)
        except Exception as e:
            print(f"Error saat mengambil artikel dari {url}: {str(e)}")
            raise

def main():
    # Baca artikel yang sudah ada
    try:
        with open("articles.json", "r", encoding="utf-8") as f:
            existing_articles = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_articles = []
    
    # Batasi jumlah halaman yang akan di-scrape (0 = unlimited)
    max_pages = 10  # Ubah nilai ini sesuai kebutuhan
    
    # Simpan URL yang sudah ada
    existing_urls = {article['url'] for article in existing_articles}
    
    # Ambil URL artikel baru dengan batasan halaman
    urls = scrape_article_list(max_pages)
    
    # Proses hanya artikel yang belum ada
    new_articles = []
    for url in urls:
        if url not in existing_urls:
            try:
                article = scrape_article_detail(url)
                new_articles.append(article)
                print(f"Berhasil menambahkan artikel: {article['judul']}")
            except Exception as e:
                print(f"Gagal mengambil artikel dari {url}: {str(e)}")
    
    # Gabungkan artikel lama dan baru
    all_articles = existing_articles + new_articles
    
    # Simpan kembali ke file
    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal artikel yang sudah ada: {len(existing_articles)}")
    print(f"Artikel baru yang ditambahkan: {len(new_articles)}")
    print(f"Total artikel sekarang: {len(all_articles)}")


if __name__ == "__main__":
    main()
