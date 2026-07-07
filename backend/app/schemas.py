from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# Auth Schemas
class UserBase(BaseModel):
    username: Optional[str] = None
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = "manager"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    google_id: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime
    last_login: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class GoogleLogin(BaseModel):
    credential: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None


# Supplier Schemas
class SupplierBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    performance_score: Optional[float] = 90.0
    status: Optional[str] = "active"

class SupplierResponse(SupplierBase):
    id: int

    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    name: str
    category: str
    sku: str
    barcode: Optional[str] = None
    image_url: Optional[str] = None
    price: float
    description: Optional[str] = None
    supplier_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    supplier_id: Optional[int] = None

# Batch Schemas
class BatchBase(BaseModel):
    product_id: int
    batch_number: str
    quantity: int
    initial_quantity: int
    manufacture_date: datetime
    expiry_date: datetime
    cost_price: float
    storage_location: Optional[str] = None
    temperature_controlled: Optional[bool] = False

class BatchCreate(BatchBase):
    pass

class BatchUpdate(BaseModel):
    quantity: Optional[int] = None
    status: Optional[str] = None
    storage_location: Optional[str] = None

class BatchResponse(BatchBase):
    id: int
    status: str
    days_to_expiry: Optional[int] = None  # Calculated dynamically
    risk_level: Optional[str] = None      # Calculated dynamically (critical, warning, safe)
    progress_percentage: Optional[float] = None # Calculated shelf life percentage

    class Config:
        from_attributes = True

# Combined Product and Batches response
class ProductResponse(ProductBase):
    id: int
    carbon_footprint_saved: float
    food_waste_saved: float
    supplier: Optional[SupplierResponse] = None
    batches: List[BatchResponse] = []
    total_quantity: Optional[int] = 0

    class Config:
        from_attributes = True


# Sale Schemas
class SaleBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    total_price: float

class SaleCreate(BaseModel):
    product_id: int
    quantity: int

class SaleResponse(SaleBase):
    id: int
    timestamp: datetime
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


# Recommendation Schemas
class RecommendationResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    batch_id: Optional[int] = None
    batch_number: Optional[str] = None
    type: str
    title: str
    description: str
    details: Optional[str] = None
    potential_savings: float
    discount_percent: Optional[float] = None
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True


# Alert Schemas
class AlertResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    batch_id: Optional[int] = None
    batch_number: Optional[str] = None
    severity: str
    message: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Query/Copilot Schemas
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    category: str
    timestamp: datetime

# Time Simulator Schemas
class SimulationTimeShift(BaseModel):
    days: int

class SimulationStatus(BaseModel):
    virtual_date: datetime
    days_offset: int
