from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String)
    role = Column(String, default="manager") # manager, supervisor, clerk
    is_active = Column(Boolean, default=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    profile_picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_person = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    performance_score = Column(Float, default=90.0) # score from 0-100
    status = Column(String, default="active") # active, inactive
    
    products = relationship("Product", back_populates="supplier")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True) # e.g. Pharmacy, Dairy, Bakery, Fresh Produce
    sku = Column(String, unique=True, index=True, nullable=False)
    barcode = Column(String, unique=True, index=True, nullable=True)
    image_url = Column(String, nullable=True)
    price = Column(Float, nullable=False) # retail price
    description = Column(Text, nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    
    # Sustainability tracking
    carbon_footprint_saved = Column(Float, default=0.0) # in kg CO2
    food_waste_saved = Column(Float, default=0.0) # in kg
    
    supplier = relationship("Supplier", back_populates="products")
    batches = relationship("Batch", back_populates="product", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="product", cascade="all, delete-orphan")

class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_number = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0) # current stock quantity
    initial_quantity = Column(Integer, nullable=False) # starting quantity
    manufacture_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False, index=True)
    cost_price = Column(Float, nullable=False) # cost price from supplier
    storage_location = Column(String, nullable=True) # Aisle, Shelf, Fridge
    temperature_controlled = Column(Boolean, default=False)
    status = Column(String, default="active") # active, empty, written_off
    
    product = relationship("Product", back_populates="batches")
    recommendations = relationship("Recommendation", back_populates="batch", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="batch", cascade="all, delete-orphan")

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="sales")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    type = Column(String, nullable=False) # discount, transfer, delay_reorder, dead_stock
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    details = Column(String, nullable=True) # JSON or additional metadata
    potential_savings = Column(Float, default=0.0)
    discount_percent = Column(Float, nullable=True)
    status = Column(String, default="pending") # pending, applied, dismissed
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="recommendations")
    batch = relationship("Batch", back_populates="recommendations")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    severity = Column(String, nullable=False) # critical, warning, info
    message = Column(String, nullable=False)
    status = Column(String, default="active") # active, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="alerts")
    batch = relationship("Batch", back_populates="alerts")

class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False)
    response = Column(Text, nullable=False)
    category = Column(String, default="copilot") # copilot, text-to-sql
    timestamp = Column(DateTime, default=datetime.utcnow)
