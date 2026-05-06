from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List
import time

# Disable OpenAPI documentation (Swagger/Redoc) to avoid unnecessary overhead during tests
app = FastAPI(docs_url=None, redoc_url=None)

# Data structure definitions for request and response
class Item(BaseModel):
    id: int
    name: str

class ProcessedItem(Item):
    processedAt: int

# =========================================================
# ENDPOINT 1: Minimal Routing & Concurrency Test
# Used for Scenarios 1 & 3 to test pure throughput and connection limits
# =========================================================
@app.get("/io")
async def minimal_routing():
    # Immediate response to test raw connection handling and routing speed
    return {"status": "ok"}

# =========================================================
# ENDPOINT 2: JSON Processing & CPU/Memory Overhead Test
# Used for Scenario 2
# =========================================================
@app.post("/json", response_model=List[ProcessedItem])
async def process_json(items: List[Item], authorization: str = Header(None)):
    # 1. Header verification
    if authorization != "Bearer secret-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # 2. Business transformation 
    now = int(time.time() * 1000)
    
    # Create a new list, mapping objects and appending a timestamp
    processed = [
        ProcessedItem(**item.model_dump(), processedAt=now) for item in items
    ]
    
    return processed