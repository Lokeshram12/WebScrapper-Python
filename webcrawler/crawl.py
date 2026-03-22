from urllib.parse import urlparse
from bs4 import BeautifulSoup

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    
    netloc = parsed.netloc
    path = parsed.path
    
    # Combine domain and path
    return netloc + path

def get_heading_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)

    h2 = soup.find('h2')
    if h2:
        return h2.get_text(strip=True)

    return None

def get_first_paragraph_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Try to find <main> first
    main = soup.find('main')
    if main:
        p = main.find('p')
        if p:
            return p.get_text(strip=True)

    # Fallback: first <p> anywhere
    p = soup.find('p')
    if p:
        return p.get_text(strip=True)

    return ""