import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import create_document, get_documents
from schemas import Message

app = FastAPI(title="Musician Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Musician Portfolio Backend is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

# Public content endpoints (static for now, could be moved to DB later)

class Track(BaseModel):
    title: str
    url: str  # streaming/embed URL
    duration: str

class Gig(BaseModel):
    date: str
    venue: str
    city: str

SAMPLE_TRACKS = [
    Track(title="Neon Skyline", url="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/91501621", duration="3:42"),
    Track(title="Midnight Drive", url="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/91501622", duration="4:05"),
]

SAMPLE_GIGS = [
    Gig(date="2025-12-04", venue="Electric Ballroom", city="London"),
    Gig(date="2026-01-12", venue="The Echo", city="Los Angeles"),
]

@app.get("/api/tracks", response_model=List[Track])
def get_tracks():
    return SAMPLE_TRACKS

@app.get("/api/gigs", response_model=List[Gig])
def get_gigs():
    return SAMPLE_GIGS

# Contact form endpoint with MongoDB persistence
@app.post("/api/contact")
def submit_contact(message: Message):
    try:
        inserted_id = create_document("message", message)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
