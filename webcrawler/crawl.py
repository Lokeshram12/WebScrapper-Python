from urllib.parse import urlparse,urljoin
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

def get_urls_from_html(html, base_url):
    try:
        soup = BeautifulSoup(html, "html.parser")
        urls = []

        # Find all <a> tags
        for tag in soup.find_all("a"):
            href = tag.get("href")
            if href:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                urls.append(absolute_url)

        return urls
    except Exception as e:
        return [], e

def get_images_from_html(html, base_url):
    try:
        soup = BeautifulSoup(html, "html.parser")
        images = []

        # Find all <img> tags
        for tag in soup.find_all("img"):
            src = tag.get("src")  # safely get src attribute
            if src:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, src)
                images.append(absolute_url)

        return images
    except Exception as e:
        return [], e

def extract_page_data(html, page_url):
    heading = get_heading_from_html(html)
    first_paragraph = get_first_paragraph_from_html(html)
    outgoing_links = get_urls_from_html(html, page_url)
    image_urls = get_images_from_html(html, page_url)

    return {
        "url": page_url,
        "heading": heading,
        "first_paragraph": first_paragraph,
        "outgoing_links": outgoing_links,
        "image_urls": image_urls
    }