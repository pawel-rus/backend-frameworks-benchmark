from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
from typing import List

# Disable Swagger/OpenAPI docs
app = FastAPI(docs_url=None, redoc_url=None)


# =========================================================
# DTO for Scenario 2
# =========================================================
class Item(BaseModel):
    id: int
    name: str
    quantity: int

# =========================================================
# Scenario 1
# Minimal routing benchmark
# =========================================================
@app.get("/io")
async def minimal_routing():
    return PlainTextResponse("OKAY", status_code=200)


# =========================================================
# Scenario 2
# JSON serialization/deserialization benchmark
# =========================================================
@app.post("/json", response_model=List[Item])
async def process_json(items: List[Item]):

    processed = [
        Item(
            id=item.id,
            name=item.name.upper(),
            quantity=item.quantity + 1
        )
        for item in items
    ]

    return processed


# =========================================================
# Scenario 3
# Exception handling benchmark
# =========================================================
@app.post("/exceptions")
async def process_exceptions(
    authorization: str = Header(default=None)
):

    if authorization != "Bearer secret-token":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized access to endpoint. Either no, or invalid bearer token provided"
        )

    return PlainTextResponse("OKAY", status_code=200)
