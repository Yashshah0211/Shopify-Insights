import json
from app.storage.db import SessionLocal, engine, Base
from app.storage.models import Brand
from app.schema import BrandContext
import os

# create tables if not exist
Base.metadata.create_all(bind=engine)

def save_brand_context_optional(ctx: BrandContext):
    # ctx may be pydantic model or dict
    data = ctx.dict() if hasattr(ctx, 'dict') else dict(ctx)
    website = data.get('website')
    if not website:
        return
    db = SessionLocal()
    try:
        rec = db.query(Brand).filter_by(website=website).first()
        if not rec:
            rec = Brand(website=website, json=json.dumps(data))
            db.add(rec)
        else:
            rec.json = json.dumps(data)
        db.commit()
    finally:
        db.close()
