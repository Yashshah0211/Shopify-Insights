# Shopify Insights Fetcher (Ready-to-run)

## What this includes
- FastAPI app that fetches Shopify store insights (no official Shopify API)
- Mandatory features: product catalog, hero products, policies, FAQs, socials, contact, about, important links
- Bonus features:
  - Competitor analysis endpoint (simple web-search using DuckDuckGo via https://duckduckgo.com/html/)
  - Persistence: SQLAlchemy-based; default uses SQLite. To use MySQL, set DB_URL environment variable (e.g. mysql+pymysql://user:pass@host:3306/dbname)

## Run locally
1. Create and activate virtual env
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # or .\.venv\Scripts\Activate.ps1 on Windows PowerShell
   pip install -r requirements.txt
   ```
2. Run the app
   ```bash
   python -m uvicorn app.main:app --reload
   ```
3. Open docs: http://127.0.0.1:8000/docs

## Files
- app/main.py          -> FastAPI entry
- app/schema.py        -> Pydantic models
- app/services/insights.py -> scraping + orchestration
- app/utils/scraper.py -> helpers for scraping & extraction
- app/storage/*        -> optional persistence (SQLAlchemy)
- requirements.txt
