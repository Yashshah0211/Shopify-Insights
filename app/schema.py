from typing import List, Optional, Dict
from pydantic import BaseModel, AnyUrl

class Product(BaseModel):
    title: str
    handle: Optional[str] = None
    url: Optional[AnyUrl] = None
    price: Optional[str] = None
    currency: Optional[str] = None
    images: List[Optional[AnyUrl]] = []
    sku: Optional[str] = None
    availability: Optional[str] = None
    tags: List[str] = []

class Policy(BaseModel):
    type: str
    url: Optional[AnyUrl] = None
    content: Optional[str] = None

class FAQ(BaseModel):
    question: str
    answer: Optional[str] = None
    url: Optional[AnyUrl] = None

class SocialHandles(BaseModel):
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    tiktok: Optional[str] = None
    twitter: Optional[str] = None
    youtube: Optional[str] = None
    linkedin: Optional[str] = None
    others: Dict[str, str] = {}

class Contact(BaseModel):
    emails: List[str] = []
    phones: List[str] = []
    address: Optional[str] = None
    contact_page: Optional[str] = None

class BrandLinks(BaseModel):
    order_tracking: Optional[str] = None
    contact_us: Optional[str] = None
    blog: Optional[str] = None
    about: Optional[str] = None
    sitemap: Optional[str] = None
    other_links: Dict[str, str] = {}

class BrandContext(BaseModel):
    website: AnyUrl
    detected_platform: Optional[str] = None
    whole_catalog: List[Product] = []
    hero_products: List[Product] = []
    policies: List[Policy] = []
    faqs: List[FAQ] = []
    socials: SocialHandles
    contact: Contact
    brand_text: Optional[str] = None
    links: BrandLinks
