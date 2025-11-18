"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# ----------------- App Schemas -----------------

class Category(BaseModel):
    """
    Categories collection schema
    Collection name: "category"
    """
    name: str = Field(..., description="Category name, e.g., Groceries, Rent")
    color: Optional[str] = Field(None, description="Hex color like #22c55e")
    icon: Optional[str] = Field(None, description="Icon identifier for UI usage")

class Budget(BaseModel):
    """
    Budgets collection schema
    Collection name: "budget"
    """
    category: str = Field(..., description="Category this budget applies to")
    limit: float = Field(..., ge=0, description="Spending limit for the period")
    period: str = Field("monthly", description="Budget period: monthly/weekly/annual")
    start_date: Optional[date] = Field(None, description="Start date for the budget period")

class Transaction(BaseModel):
    """
    Transactions collection schema
    Collection name: "transaction"
    """
    date: date = Field(..., description="Transaction date")
    amount: float = Field(..., description="Positive number; type determines inflow/outflow")
    type: str = Field(..., description="expense or income")
    category: str = Field(..., description="Category name")
    merchant: Optional[str] = Field(None, description="Merchant or source")
    account: Optional[str] = Field(None, description="Account used")
    notes: Optional[str] = Field(None, description="Additional notes")
    tags: Optional[List[str]] = Field(default=None, description="Optional tag labels")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
