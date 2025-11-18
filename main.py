import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import db, create_document, get_documents

app = FastAPI(title="Finance Budgeting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------- Models for requests -----------------
class TransactionIn(BaseModel):
    date: datetime
    amount: float
    type: str = Field(..., pattern="^(expense|income)$")
    category: str
    merchant: Optional[str] = None
    account: Optional[str] = None
    notes: Optional[str] = None


class BudgetIn(BaseModel):
    category: str
    limit: float
    period: str = Field("monthly")


# ----------------- Routes -----------------
@app.get("/")
async def root():
    return {"message": "Finance Budgeting API is running"}


@app.get("/api/transactions")
async def list_transactions(limit: int = 100):
    try:
        docs = get_documents("transaction", {}, limit)
        # Convert ObjectId and datetime to str
        for d in docs:
            d["_id"] = str(d.get("_id"))
            if isinstance(d.get("date"), datetime):
                d["date"] = d["date"].isoformat()
            if isinstance(d.get("created_at"), datetime):
                d["created_at"] = d["created_at"].isoformat()
            if isinstance(d.get("updated_at"), datetime):
                d["updated_at"] = d["updated_at"].isoformat()
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/transactions")
async def add_transaction(payload: TransactionIn):
    try:
        data = payload.model_dump()
        inserted_id = create_document("transaction", data)
        return {"id": inserted_id, "ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/budgets")
async def list_budgets(limit: int = 50):
    try:
        docs = get_documents("budget", {}, limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
            if isinstance(d.get("created_at"), datetime):
                d["created_at"] = d["created_at"].isoformat()
            if isinstance(d.get("updated_at"), datetime):
                d["updated_at"] = d["updated_at"].isoformat()
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/budgets")
async def add_budget(payload: BudgetIn):
    try:
        data = payload.model_dump()
        inserted_id = create_document("budget", data)
        return {"id": inserted_id, "ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
async def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, "name", "✅ Connected")
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
