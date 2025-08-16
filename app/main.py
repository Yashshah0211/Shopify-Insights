from fastapi import FastAPI, Query
from typing import Optional
from app.schema import BrandContext
from app.services.insights import build_brand_context

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Original POST endpoint
@app.post("/fetch-insights", response_model=BrandContext)
def fetch_insights_post(payload: dict):
    website_url = payload.get("website_url")
    if not website_url:
        return {"error": "website_url is required"}
    return build_brand_context(website_url)

# New GET endpoint for easier testing in browser
@app.get("/fetch-insights", response_model=BrandContext)
def fetch_insights_get(website_url: str = Query(..., description="Shopify store URL")):
    return build_brand_context(website_url)
