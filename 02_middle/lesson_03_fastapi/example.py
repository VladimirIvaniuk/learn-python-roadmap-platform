"""
Урок Middle 3 — Мінімальний FastAPI додаток з усіма ключовими концепціями

Запуск:
    pip install fastapi uvicorn pydantic[email]
    python example.py
    або: uvicorn example:app --reload

Документація: http://localhost:8000/docs
"""
from fastapi import FastAPI, HTTPException, Depends, Request, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Annotated
from datetime import datetime
import time
import uuid

app = FastAPI(title="Learn Python API Example", version="1.0")

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
    return response

# ── Schemas ───────────────────────────────────────────────────────────────────
class ItemCreate(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=200)]
    description: str | None = None
    price: Annotated[float, Field(gt=0)]
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        return v.strip()

class ItemResponse(BaseModel):
    id: int
    title: str
    description: str | None
    price: float
    tags: list[str]
    created_at: datetime

class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: Annotated[float, Field(gt=0)] | None = None

# ── In-Memory "DB" ────────────────────────────────────────────────────────────
_items: dict[int, dict] = {}
_next_id = 1

def get_db():
    return _items

# ── Exception Handlers ────────────────────────────────────────────────────────
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": [{"field": e["loc"][-1], "msg": e["msg"]} for e in exc.errors()]
        }
    )

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/items/", response_model=list[ItemResponse])
async def list_items(
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 10,
    min_price: float | None = None,
    db: dict = Depends(get_db),
):
    items = list(db.values())
    if min_price is not None:
        items = [i for i in items if i["price"] >= min_price]
    start = (page - 1) * per_page
    return items[start:start + per_page]

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: Annotated[int, Path(gt=0)],
    db: dict = Depends(get_db),
):
    item = db.get(item_id)
    if not item:
        raise HTTPException(404, f"Item {item_id} not found")
    return item

@app.post("/items/", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate, db: dict = Depends(get_db)):
    global _next_id
    new_item = {
        "id": _next_id,
        **item.model_dump(),
        "created_at": datetime.utcnow(),
    }
    db[_next_id] = new_item
    _next_id += 1
    return new_item

@app.patch("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    update: ItemUpdate,
    db: dict = Depends(get_db),
):
    item = db.get(item_id)
    if not item:
        raise HTTPException(404, f"Item {item_id} not found")
    # Оновлюємо тільки передані поля
    for field, value in update.model_dump(exclude_unset=True).items():
        item[field] = value
    return item

@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int, db: dict = Depends(get_db)):
    if item_id not in db:
        raise HTTPException(404, f"Item {item_id} not found")
    del db[item_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
