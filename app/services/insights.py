from typing import List, Dict
from urllib.parse import urljoin
from app.utils.scraper import origin, safe_get_text, try_products_json, extract_jsonld_products, extract_footer_links, find_emails_phones_socials, extract_faq_pairs, is_shopify
from app.schema import BrandContext, Product, Policy, FAQ, SocialHandles, Contact, BrandLinks
import requests

def build_brand_context(website: str) -> BrandContext:
    if not website.startswith('http'):
        website = 'https://' + website
    base = origin(website)
    # detect
    try:
        homepage = safe_get_text(base)
    except Exception as e:
        raise ValueError('Website not reachable')
    if not is_shopify(base, homepage):
        raise ValueError('Website does not appear to be a Shopify store')

    # whole catalog
    raw_products = try_products_json(base)
    products=[]
    for p in raw_products:
        products.append(Product(
            title=p.get('title') or '',
            handle=p.get('handle'),
            url=urljoin(base, f"/products/{p.get('handle')}") if p.get('handle') else None,
            images=[i.get('src') for i in p.get('images', []) if isinstance(i, dict)],
            tags=(p.get('tags') or '').split(',') if p.get('tags') else []
        ))

    # hero products: try JSON-LD on homepage
    heroes=[]
    jl = extract_jsonld_products(homepage)
    for p in jl[:6]:
        heroes.append(Product(title=p.get('title') or '', images=p.get('images', []), price=p.get('price')))

    # policies
    footer = extract_footer_links(homepage)
    policy_candidates = footer.get('policy', []) + [
        '/policies/privacy-policy','/policies/refund-policy','/policies/return-policy','/policies/terms-of-service'
    ]
    policies=[]
    seen=set()
    for rel in policy_candidates:
        url = rel if rel.startswith('http') else urljoin(base, rel)
        try:
            txt = safe_get_text(url)
            ptype = 'policy'
            if 'privacy' in url: ptype='privacy'
            if 'refund' in url: ptype='refund'
            if 'return' in url: ptype='return'
            if ptype not in seen:
                policies.append(Policy(type=ptype, url=url, content=txt[:4000]))
                seen.add(ptype)
        except Exception:
            continue

    # FAQs
    faqs=[]
    for rel in footer.get('faq', []) + ['/pages/faq','/pages/faqs','/faq','/faqs']:
        url = rel if rel.startswith('http') else urljoin(base, rel)
        try:
            html = safe_get_text(url)
            for qa in extract_faq_pairs(html):
                qa['url'] = url
                faqs.append(FAQ(**qa))
        except Exception:
            continue

    # brand text & links
    about_url = None
    for a in footer.get('about', []):
        about_url = a if a.startswith('http') else urljoin(base, a)
        break
    about_text = None
    if about_url:
        try:
            about_text = safe_get_text(about_url)[:3000]
        except Exception:
            about_text = None

    links = BrandLinks(
        order_tracking=(footer.get('track',[None]) or [None])[0],
        contact_us=(footer.get('contact',[None]) or [None])[0],
        blog=(footer.get('blog',[None]) or [None])[0],
        about=about_url,
        sitemap=(footer.get('sitemap',[urljoin(base,'/sitemap.xml')]) or [None])[0],
        other_links={}
    )

    # contact + socials
    contact_blob = homepage
    if links.contact_us:
        try:
            contact_blob += '\n' + safe_get_text(links.contact_us)
        except Exception:
            pass
    emails, phones, socials = find_emails_phones_socials(contact_blob)
    contact = Contact(emails=emails, phones=phones, contact_page=links.contact_us)
    socials_obj = SocialHandles(
        instagram=socials.get('instagram'),
        facebook=socials.get('facebook'),
        tiktok=socials.get('tiktok'),
        twitter=socials.get('twitter'),
        youtube=socials.get('youtube'),
        linkedin=socials.get('linkedin'),
        others={}
    )

    return BrandContext(
        website=base,
        detected_platform='shopify',
        whole_catalog=products,
        hero_products=heroes,
        policies=policies,
        faqs=faqs,
        socials=socials_obj,
        contact=contact,
        brand_text=about_text,
        links=links
    )

def analyze_competitors(seed_url: str, max_results: int = 3) -> List[str]:
    """Simple competitor discovery using DuckDuckGo HTML search for 'competitors' and 'similar' phrasing."""
    if not seed_url.startswith('http'):
        seed_url = 'https://' + seed_url
    # derive brand name
    try:
        r = requests.get(seed_url, timeout=8, headers={'User-Agent':'Mozilla/5.0'})
        r.raise_for_status()
        soup = None
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, 'lxml')
        except Exception:
            pass
        brand = ''
        if soup and soup.title:
            brand = soup.title.string.split('|')[0].strip()
    except Exception:
        brand = ''
    query = f"{brand} similar stores" if brand else "shopify similar stores"
    ddg = 'https://duckduckgo.com/html/'
    params = {'q': query}
    try:
        resp = requests.post(ddg, data=params, headers={'User-Agent':'Mozilla/5.0'}, timeout=10)
        resp.raise_for_status()
        links = []
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, 'lxml')
        for a in soup.select('a[href]'):
            href = a['href']
            # duckduckgo returns redirect params; filter obvious external links
            if href.startswith('http') and 'shopify' in href:
                links.append(href)
            if len(links) >= max_results:
                break
        # normalize simple forms to origins
        origins = []
        from urllib.parse import urlparse
        for l in links:
            p = urlparse(l)
            origins.append(f"{p.scheme}://{p.netloc}")
        return list(dict.fromkeys(origins))[:max_results]
    except Exception:
        return []
