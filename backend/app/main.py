from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json

from .config import settings, get_virtual_days_offset, set_virtual_days_offset
from .database import engine, Base, get_db
from . import models, schemas, crud, auth, ai_service
from .data_seeder import seed_db

# Create DB Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event: seed database if empty
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        # Check if users table is empty
        user_count = db.query(models.User).count()
        if user_count == 0:
            print("Database is empty. Seeding initial data...")
            seed_db()
    except Exception as e:
        print(f"Error checking/seeding database on startup: {e}")
    finally:
        db.close()

# ----------------- AUTH ROUTER -----------------
@app.post(f"{settings.API_V1_STR}/auth/register", response_model=schemas.Token)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create user
    user = crud.create_user(db, user_in)
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@app.post(f"{settings.API_V1_STR}/auth/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=user_in.username)
    if not user or not auth.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@app.post(f"{settings.API_V1_STR}/auth/google", response_model=schemas.Token)
def google_login(google_in: schemas.GoogleLogin, db: Session = Depends(get_db)):
    # Verify Google token
    idinfo = auth.verify_google_token(google_in.credential)
    
    google_id = idinfo["sub"]
    email = idinfo["email"]
    full_name = idinfo.get("name", "")
    profile_picture = idinfo.get("picture", "")
    
    # Check if user exists by google_id
    user = crud.get_user_by_google_id(db, google_id=google_id)
    
    if not user:
        # Check if user exists by email
        user = crud.get_user_by_email(db, email=email)
        if user:
            # Link Google account to existing user
            user.google_id = google_id
            user.profile_picture = profile_picture
            user.last_login = datetime.utcnow()
            db.commit()
            db.refresh(user)
        else:
            # Create new user
            user = crud.create_google_user(
                db,
                google_id=google_id,
                email=email,
                full_name=full_name,
                profile_picture=profile_picture
            )
    else:
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
    
    # Create access token using google_id as sub
    access_token = auth.create_access_token(data={"sub": user.google_id or user.username})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@app.get(f"{settings.API_V1_STR}/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user


# ----------------- DASHBOARD ROUTER -----------------
@app.get(f"{settings.API_V1_STR}/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    return crud.get_dashboard_stats(db)

@app.get(f"{settings.API_V1_STR}/dashboard/forecast")
def get_forecast(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    return crud.get_forecasts(db)


# ----------------- PRODUCTS ROUTER -----------------
@app.get(f"{settings.API_V1_STR}/products", response_model=List[schemas.ProductResponse])
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    virtual_now = crud.get_virtual_now()
    db_products = crud.get_products(db, category=category, search=search)
    
    enriched_products = []
    for p in db_products:
        # Calculate total quantity and enrich batches
        batches = [crud.enrich_batch_response(b, virtual_now) for b in p.batches if b.quantity > 0]
        total_qty = sum(b.quantity for b in batches)
        
        enriched_p = schemas.ProductResponse(
            id=p.id,
            name=p.name,
            category=p.category,
            sku=p.sku,
            barcode=p.barcode,
            image_url=p.image_url,
            price=p.price,
            description=p.description,
            supplier_id=p.supplier_id,
            carbon_footprint_saved=p.carbon_footprint_saved,
            food_waste_saved=p.food_waste_saved,
            supplier=p.supplier,
            batches=batches,
            total_quantity=total_qty
        )
        enriched_products.append(enriched_p)
        
    return enriched_products

@app.get(f"{settings.API_V1_STR}/products/{{product_id}}", response_model=schemas.ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    virtual_now = crud.get_virtual_now()
    p = crud.get_product(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
        
    batches = [crud.enrich_batch_response(b, virtual_now) for b in p.batches if b.quantity > 0]
    total_qty = sum(b.quantity for b in batches)
    
    return schemas.ProductResponse(
        id=p.id,
        name=p.name,
        category=p.category,
        sku=p.sku,
        barcode=p.barcode,
        image_url=p.image_url,
        price=p.price,
        description=p.description,
        supplier_id=p.supplier_id,
        carbon_footprint_saved=p.carbon_footprint_saved,
        food_waste_saved=p.food_waste_saved,
        supplier=p.supplier,
        batches=batches,
        total_quantity=total_qty
    )

@app.post(f"{settings.API_V1_STR}/products", response_model=schemas.ProductResponse)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Check if SKU already exists
    existing = db.query(models.Product).filter(models.Product.sku == product_in.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    p = crud.create_product(db, product_in)
    return get_product(p.id, db, current_user)

@app.put(f"{settings.API_V1_STR}/products/{{product_id}}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product_in: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    p = crud.update_product(db, product_id, product_in)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return get_product(product_id, db, current_user)


# ----------------- BATCHES ROUTER -----------------
@app.get(f"{settings.API_V1_STR}/batches", response_model=List[schemas.BatchResponse])
def get_batches(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    virtual_now = crud.get_virtual_now()
    db_batches = crud.get_batches(db)
    return [crud.enrich_batch_response(b, virtual_now) for b in db_batches]

@app.post(f"{settings.API_V1_STR}/batches", response_model=schemas.BatchResponse)
def create_batch(
    batch_in: schemas.BatchCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_batch = crud.create_batch(db, batch_in)
    virtual_now = crud.get_virtual_now()
    return crud.enrich_batch_response(db_batch, virtual_now)

@app.put(f"{settings.API_V1_STR}/batches/{{batch_id}}", response_model=schemas.BatchResponse)
def update_batch(
    batch_id: int,
    batch_in: schemas.BatchUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_batch = crud.update_batch(db, batch_id, batch_in)
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    virtual_now = crud.get_virtual_now()
    return crud.enrich_batch_response(db_batch, virtual_now)


# ----------------- SALES ROUTER -----------------
@app.post(f"{settings.API_V1_STR}/sales", response_model=schemas.SaleResponse)
def record_sale(
    sale_in: schemas.SaleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_sale = crud.create_sale(db, sale_in)
    if not db_sale:
        raise HTTPException(status_code=400, detail="Insufficient FEFO stock available for this sale.")
    
    # Enrich response
    response_sale = schemas.SaleResponse(
        id=db_sale.id,
        product_id=db_sale.product_id,
        quantity=db_sale.quantity,
        unit_price=db_sale.unit_price,
        total_price=db_sale.total_price,
        timestamp=db_sale.timestamp,
        product_name=db_sale.product.name
    )
    return response_sale

@app.get(f"{settings.API_V1_STR}/sales", response_model=List[schemas.SaleResponse])
def get_sales(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    sales = db.query(models.Sale).order_by(models.Sale.timestamp.desc()).limit(50).all()
    enriched = []
    for s in sales:
        enriched.append(schemas.SaleResponse(
            id=s.id,
            product_id=s.product_id,
            quantity=s.quantity,
            unit_price=s.unit_price,
            total_price=s.total_price,
            timestamp=s.timestamp,
            product_name=s.product.name
        ))
    return enriched


# ----------------- RECOMMENDATIONS ROUTER -----------------
@app.get(f"{settings.API_V1_STR}/recommendations", response_model=List[schemas.RecommendationResponse])
def get_recommendations(
    status: Optional[str] = "pending",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    recs = crud.get_recommendations(db, status=status)
    response_recs = []
    for r in recs:
        response_recs.append(schemas.RecommendationResponse(
            id=r.id,
            product_id=r.product_id,
            product_name=r.product.name,
            batch_id=r.batch_id,
            batch_number=r.batch.batch_number if r.batch else None,
            type=r.type,
            title=r.title,
            description=r.description,
            details=r.details,
            potential_savings=r.potential_savings,
            discount_percent=r.discount_percent,
            status=r.status,
            timestamp=r.timestamp
        ))
    return response_recs

@app.post(f"{settings.API_V1_STR}/recommendations/{{rec_id}}/apply", response_model=schemas.RecommendationResponse)
def apply_rec(
    rec_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    r = crud.apply_recommendation(db, rec_id)
    if not r:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    return schemas.RecommendationResponse(
        id=r.id,
        product_id=r.product_id,
        product_name=r.product.name,
        batch_id=r.batch_id,
        batch_number=r.batch.batch_number if r.batch else None,
        type=r.type,
        title=r.title,
        description=r.description,
        details=r.details,
        potential_savings=r.potential_savings,
        discount_percent=r.discount_percent,
        status=r.status,
        timestamp=r.timestamp
    )

@app.post(f"{settings.API_V1_STR}/recommendations/{{rec_id}}/dismiss", response_model=schemas.RecommendationResponse)
def dismiss_rec(
    rec_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    r = crud.dismiss_recommendation(db, rec_id)
    if not r:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return schemas.RecommendationResponse(
        id=r.id,
        product_id=r.product_id,
        product_name=r.product.name,
        batch_id=r.batch_id,
        batch_number=r.batch.batch_number if r.batch else None,
        type=r.type,
        title=r.title,
        description=r.description,
        details=r.details,
        potential_savings=r.potential_savings,
        discount_percent=r.discount_percent,
        status=r.status,
        timestamp=r.timestamp
    )


# ----------------- ALERTS ROUTER -----------------
@app.get(f"{settings.API_V1_STR}/alerts", response_model=List[schemas.AlertResponse])
def get_alerts(
    status: Optional[str] = "active",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    alerts = crud.get_alerts(db, status=status)
    response_alerts = []
    for a in alerts:
        response_alerts.append(schemas.AlertResponse(
            id=a.id,
            product_id=a.product_id,
            product_name=a.product.name,
            batch_id=a.batch_id,
            batch_number=a.batch.batch_number if a.batch else None,
            severity=a.severity,
            message=a.message,
            status=a.status,
            created_at=a.created_at
        ))
    return response_alerts


# ----------------- COPILOT ROUTER -----------------
@app.post(f"{settings.API_V1_STR}/copilot/chat")
def chat_copilot(
    req: schemas.QueryRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    response_text = ai_service.ask_copilot(db, req.query)
    
    # Save in query history
    qh = models.QueryHistory(query=req.query, response=response_text, category="copilot")
    db.add(qh)
    db.commit()
    
    return {"response": response_text, "category": "copilot", "timestamp": qh.timestamp}

@app.post(f"{settings.API_V1_STR}/copilot/sql")
def sql_copilot(
    req: schemas.QueryRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    sql_data = ai_service.translate_text_to_sql(req.query)
    
    qh = models.QueryHistory(query=req.query, response=json.dumps(sql_data), category="text-to-sql")
    db.add(qh)
    db.commit()
    
    return {
        "sql": sql_data.get("sql"),
        "explanation": sql_data.get("explanation"),
        "target_table": sql_data.get("target_table"),
        "timestamp": qh.timestamp
    }

@app.post(f"{settings.API_V1_STR}/copilot/ocr")
async def ocr_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    content = await file.read()
    extracted_data = ai_service.parse_ocr_label(content, file.filename)
    return extracted_data


# ----------------- TIME SIMULATOR ROUTER -----------------
@app.post(f"{settings.API_V1_STR}/simulation/shift", response_model=schemas.SimulationStatus)
def shift_time(
    req: schemas.SimulationTimeShift,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Triggers shift of offset days, runs health check and alerts updates
    v_date, offset = crud.trigger_time_simulation(db, req.days)
    return schemas.SimulationStatus(virtual_date=v_date, days_offset=offset)

@app.get(f"{settings.API_V1_STR}/simulation/status", response_model=schemas.SimulationStatus)
def get_simulation_status(
    current_user: models.User = Depends(auth.get_current_active_user)
):
    v_date = crud.get_virtual_now()
    offset = get_virtual_days_offset()
    return schemas.SimulationStatus(virtual_date=v_date, days_offset=offset)

@app.post(f"{settings.API_V1_STR}/simulation/reset", response_model=schemas.SimulationStatus)
def reset_simulation(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    set_virtual_days_offset(0)
    crud.run_inventory_health_check(db)
    v_date = crud.get_virtual_now()
    return schemas.SimulationStatus(virtual_date=v_date, days_offset=0)


# ----------------- REPORTS ROUTER -----------------
@app.get(f"{settings.API_V1_STR}/reports/download")
def download_report(
    type: str, # inventory, expiry, waste, sales
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Simulated downloads. We generate beautiful clean JSON structure that 
    # the frontend client can dynamically parse and download as a CSV/Excel/PDF file!
    # This prevents complex binary generation errors while remaining extremely high-fidelity.
    virtual_now = crud.get_virtual_now()
    
    if type == "inventory":
        products = db.query(models.Product).all()
        data = []
        for p in products:
            total_qty = sum(b.quantity for b in p.batches if b.status == "active")
            data.append({
                "SKU": p.sku,
                "Product Name": p.name,
                "Category": p.category,
                "Stock Quantity": total_qty,
                "Retail Price (INR)": p.price,
                "Supplier": p.supplier.name if p.supplier else "N/A"
            })
        filename = f"inventory_report_{virtual_now.strftime('%Y%m%d')}.csv"
        return {"filename": filename, "data": data}
        
    elif type == "expiry":
        batches = db.query(models.Batch).filter(models.Batch.quantity > 0, models.Batch.status == "active").all()
        data = []
        for b in batches:
            days = (b.expiry_date - virtual_now).days
            data.append({
                "Product SKU": b.product.sku,
                "Product Name": b.product.name,
                "Batch Number": b.batch_number,
                "Stock": b.quantity,
                "Expiry Date": b.expiry_date.strftime("%Y-%m-%d"),
                "Days to Expiry": days,
                "Location": b.storage_location,
                "Risk State": "CRITICAL" if days <= 7 else ("WARNING" if days <= 30 else "SAFE")
            })
        filename = f"expiry_risk_report_{virtual_now.strftime('%Y%m%d')}.csv"
        return {"filename": filename, "data": data}
        
    elif type == "waste":
        # Sum of batches that are expired (quantity > 0 and days_to_expiry <= 0)
        batches = db.query(models.Batch).all()
        data = []
        for b in batches:
            days = (b.expiry_date - virtual_now).days
            if days <= 0 and b.quantity > 0:
                data.append({
                    "Product Name": b.product.name,
                    "Batch Number": b.batch_number,
                    "Expired Quantity": b.quantity,
                    "Cost Loss (INR)": round(b.quantity * b.cost_price, 2),
                    "Storage Location": b.storage_location,
                    "Expiry Date": b.expiry_date.strftime("%Y-%m-%d")
                })
        filename = f"waste_loss_report_{virtual_now.strftime('%Y%m%d')}.csv"
        return {"filename": filename, "data": data}
        
    elif type == "sales":
        sales = db.query(models.Sale).all()
        data = []
        for s in sales:
            data.append({
                "Timestamp": s.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "Product SKU": s.product.sku,
                "Product Name": s.product.name,
                "Quantity Sold": s.quantity,
                "Unit Price (INR)": s.unit_price,
                "Total Revenue (INR)": s.total_price
            })
        filename = f"sales_report_{virtual_now.strftime('%Y%m%d')}.csv"
        return {"filename": filename, "data": data}
        
    else:
        raise HTTPException(status_code=400, detail="Invalid report type requested.")
