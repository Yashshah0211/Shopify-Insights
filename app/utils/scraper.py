import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (InsightsFetcher)"
}

def origin(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme or 'https'}://{p.netloc}"

def safe_get_text(url: str, timeout: int = 12):
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.text

def try_products_json(base: str):
    url = urljoin(base, '/products.json?limit=250')
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code == 200:
            return r.json().get('products', [])
    except Exception:
        return []
    return []

def extract_jsonld_products(html: str):
    out=[]
    soup = BeautifulSoup(html, 'lxml')
    for tag in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(tag.string or '{}')
        except Exception:
            continue
        if isinstance(data, dict) and (data.get('@type') == 'Product' or data.get('mainEntityOfPage')== 'Product'):
            title = data.get('name')
            imgs = data.get('image') or []
            if isinstance(imgs, str): imgs=[imgs]
            offers = data.get('offers') or {}
            price = offers.get('price') if isinstance(offers, dict) else None
            out.append({'title': title, 'images': imgs, 'price': price})
    return out

def extract_footer_links(html: str):
    soup = BeautifulSoup(html, 'lxml')
    links = {}
    for a in soup.find_all('a', href=True):
        text = (a.get_text() or '').strip().lower()
        href = a['href']
        if any(k in text for k in ['privacy','refund','return','terms','shipping']):
            links.setdefault('policy', []).append(href)
        if 'faq' in text:
            links.setdefault('faq', []).append(href)
        if 'contact' in text:
            links.setdefault('contact', []).append(href)
        if 'about' in text:
            links.setdefault('about', []).append(href)
        if 'track' in text:
            links.setdefault('track', []).append(href)
        if 'blog' in text:
            links.setdefault('blog', []).append(href)
        if 'sitemap' in text:
            links.setdefault('sitemap', []).append(href)
    return links

def find_emails_phones_socials(html: str):
    emails = sorted(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html)))
    phones = sorted(set(m.group(0) for m in re.finditer(r"(\+?\d[\d\s\-().]{6,}\d)", html)))
    socials = {}
    for key, domain in [('instagram','instagram.com'),('facebook','facebook.com'),('tiktok','tiktok.com'),
                        ('twitter','twitter.com'),('youtube','youtube.com'),('linkedin','linkedin.com')]:
        m = re.search(rf"https?://(www\.)?{domain}/[^\"'<>\s]+", html, re.I)
        if m:
            socials[key]=m.group(0)
    return emails, phones, socials

def extract_faq_pairs(html: str):
    soup = BeautifulSoup(html, 'lxml')
    qas=[]
    for d in soup.find_all('details'):
        q = d.find('summary').get_text(strip=True) if d.find('summary') else ''
        a = d.get_text(' ', strip=True).replace(q, '').strip()
        if q:
            qas.append({'question': q, 'answer': a})
    # fallback: headings + next p
    for h in soup.find_all(['h2','h3','h4']):
        q = h.get_text(' ', strip=True)
        nxt = h.find_next_sibling()
        if q and nxt:
            a = nxt.get_text(' ', strip=True)
            qas.append({'question': q, 'answer': a})
    # dedupe
    seen=set(); out=[]
    for qa in qas:
        k=(qa['question'][:120], qa['answer'][:120])
        if k not in seen:
            out.append(qa); seen.add(k)
    return out

def is_shopify(base: str, homepage_html: str = None):
    try:
        html = homepage_html or safe_get_text(base)
    except Exception:
        return False
    if 'cdn.shopify.com' in html.lower():
        return True
    # test products.json
    try:
        data = try_products_json(base)
        if data:
            return True
    except Exception:
        pass
    return 'shopify' in html.lower()
