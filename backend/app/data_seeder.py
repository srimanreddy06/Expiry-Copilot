from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import SessionLocal, engine, Base
from . import models, crud
from .auth import get_password_hash

def seed_db():
    # Re-create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Seeding database...")
        
        # 1. Create Default Admin User
        admin = models.User(
            username="admin",
            email="admin@expiry-copilot.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Pharmacy Operations Director",
            role="manager"
        )
        db.add(admin)
        
        # 2. Create Suppliers
        suppliers = [
            models.Supplier(name="Global Pharma Supply Co", contact_person="John Doe", email="john@globalpharma.com", phone="+1 555-0192", performance_score=96.4),
            models.Supplier(name="Apex Fresh Foods Ltd", contact_person="Sarah Connor", email="sarah@apexfresh.com", phone="+1 555-0183", performance_score=89.2),
            models.Supplier(name="MediPlus Wholesale Inc", contact_person="Alice Smith", email="alice@mediplus.com", phone="+1 555-0144", performance_score=94.1),
            models.Supplier(name="Metro Dairy Distributors", contact_person="Bob Vance", email="bob@metrodairy.com", phone="+1 555-0155", performance_score=91.8)
        ]
        for s in suppliers:
            db.add(s)
        db.commit() # Commit suppliers to get IDs
        
        # Supplier IDs
        pharma_sup = suppliers[0].id
        food_sup = suppliers[1].id
        medi_sup = suppliers[2].id
        dairy_sup = suppliers[3].id
        
        # 3. Create Products & Batches
        now = datetime.utcnow()
        
        # Pharmacy category
        p1 = models.Product(
            name="Amoxicillin 500mg", category="Pharmacy", sku="AMX-500", barcode="8901234567890",
            image_url="https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400", price=450.00,
            description="Broad-spectrum antibiotic used to treat bacterial infections.", supplier_id=pharma_sup,
            carbon_footprint_saved=12.5, food_waste_saved=5.0
        )
        db.add(p1)
        db.commit()
        
        b1_1 = models.Batch(
            product_id=p1.id, batch_number="AMX-B101", quantity=35, initial_quantity=100,
            manufacture_date=now - timedelta(days=60), expiry_date=now + timedelta(days=5),
            cost_price=180.00, storage_location="Fridge A", temperature_controlled=True, status="active"
        )
        b1_2 = models.Batch(
            product_id=p1.id, batch_number="AMX-B102", quantity=120, initial_quantity=150,
            manufacture_date=now - timedelta(days=20), expiry_date=now + timedelta(days=90),
            cost_price=180.00, storage_location="Shelf B2", temperature_controlled=False, status="active"
        )
        db.add_all([b1_1, b1_2])
        
        p2 = models.Product(
            name="Ibuprofen 400mg", category="Pharmacy", sku="IBU-400", barcode="8901234567891",
            image_url="https://images.unsplash.com/photo-1550572017-edd951b55104?w=400", price=120.00,
            description="Nonsteroidal anti-inflammatory drug (NSAID) for pain relief.", supplier_id=medi_sup,
            carbon_footprint_saved=8.2, food_waste_saved=3.2
        )
        db.add(p2)
        db.commit()
        
        b2_1 = models.Batch(
            product_id=p2.id, batch_number="IBU-B201", quantity=15, initial_quantity=120,
            manufacture_date=now - timedelta(days=120), expiry_date=now + timedelta(days=12),
            cost_price=50.00, storage_location="Shelf B3", temperature_controlled=False, status="active"
        )
        b2_2 = models.Batch(
            product_id=p2.id, batch_number="IBU-B202", quantity=250, initial_quantity=250,
            manufacture_date=now - timedelta(days=30), expiry_date=now + timedelta(days=240),
            cost_price=50.00, storage_location="Shelf B3", temperature_controlled=False, status="active"
        )
        db.add_all([b2_1, b2_2])
        
        # Dairy category
        p3 = models.Product(
            name="Organic Whole Milk 1L", category="Dairy", sku="MLK-001", barcode="8901234567892",
            image_url="https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400", price=90.00,
            description="Pasteurized organic cow milk.", supplier_id=dairy_sup,
            carbon_footprint_saved=24.0, food_waste_saved=9.6
        )
        db.add(p3)
        db.commit()
        
        b3_1 = models.Batch(
            product_id=p3.id, batch_number="MLK-B881", quantity=22, initial_quantity=60,
            manufacture_date=now - timedelta(days=4), expiry_date=now + timedelta(days=3),
            cost_price=55.00, storage_location="Fridge A", temperature_controlled=True, status="active"
        )
        b3_2 = models.Batch(
            product_id=p3.id, batch_number="MLK-B882", quantity=48, initial_quantity=80,
            manufacture_date=now - timedelta(days=1), expiry_date=now + timedelta(days=7),
            cost_price=55.00, storage_location="Fridge A", temperature_controlled=True, status="active"
        )
        db.add_all([b3_1, b3_2])
        
        p4 = models.Product(
            name="Greek Yogurt 500g", category="Dairy", sku="YGT-500", barcode="8901234567893",
            image_url="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400", price=180.00,
            description="Plain unsweetened rich Greek yogurt.", supplier_id=dairy_sup,
            carbon_footprint_saved=15.0, food_waste_saved=6.0
        )
        db.add(p4)
        db.commit()
        
        b4_1 = models.Batch(
            product_id=p4.id, batch_number="YGT-B910", quantity=18, initial_quantity=40,
            manufacture_date=now - timedelta(days=12), expiry_date=now + timedelta(days=6),
            cost_price=110.00, storage_location="Fridge B", temperature_controlled=True, status="active"
        )
        db.add(b4_1)

        # Fresh Produce category
        p5 = models.Product(
            name="Organic Avocados Pack of 4", category="Fresh Produce", sku="AVO-004", barcode="8901234567894",
            image_url="https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=400", price=320.00,
            description="Ready-to-eat organic Haas avocados.", supplier_id=food_sup,
            carbon_footprint_saved=31.2, food_waste_saved=12.5
        )
        db.add(p5)
        db.commit()
        
        b5_1 = models.Batch(
            product_id=p5.id, batch_number="AVO-B01", quantity=14, initial_quantity=30,
            manufacture_date=now - timedelta(days=5), expiry_date=now + timedelta(days=2),
            cost_price=190.00, storage_location="Aisle 1", temperature_controlled=False, status="active"
        )
        db.add(b5_1)
        
        p6 = models.Product(
            name="Fresh Strawberries 400g", category="Fresh Produce", sku="STR-400", barcode="8901234567895",
            image_url="https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400", price=290.00,
            description="Sweet red strawberries, locally grown.", supplier_id=food_sup,
            carbon_footprint_saved=10.0, food_waste_saved=4.0
        )
        db.add(p6)
        db.commit()
        
        b6_1 = models.Batch(
            product_id=p6.id, batch_number="STR-B22", quantity=25, initial_quantity=50,
            manufacture_date=now - timedelta(days=3), expiry_date=now + timedelta(days=4),
            cost_price=160.00, storage_location="Cold Room", temperature_controlled=True, status="active"
        )
        db.add(b6_1)

        # Bakery category
        p7 = models.Product(
            name="Sourdough Bread 500g", category="Bakery", sku="SDB-500", barcode="8901234567896",
            image_url="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400", price=160.00,
            description="Artisanal sourdough loaf baked daily.", supplier_id=food_sup,
            carbon_footprint_saved=5.0, food_waste_saved=2.0
        )
        db.add(p7)
        db.commit()
        
        b7_1 = models.Batch(
            product_id=p7.id, batch_number="SDB-B44", quantity=8, initial_quantity=20,
            manufacture_date=now - timedelta(days=1), expiry_date=now + timedelta(days=1),
            cost_price=80.00, storage_location="Aisle 4", temperature_controlled=False, status="active"
        )
        b7_2 = models.Batch(
            product_id=p7.id, batch_number="SDB-B45", quantity=25, initial_quantity=25,
            manufacture_date=now, expiry_date=now + timedelta(days=4),
            cost_price=80.00, storage_location="Aisle 4", temperature_controlled=False, status="active"
        )
        db.add_all([b7_1, b7_2])
        
        # Expired items to demonstrate alerts
        p8 = models.Product(
            name="Canned Mushroom Soup 400g", category="Pantry", sku="MSR-400", barcode="8901234567897",
            image_url="https://images.unsplash.com/photo-1547592180-85f173990554?w=400", price=140.00,
            description="Creamy wild mushroom condensed soup.", supplier_id=food_sup,
            carbon_footprint_saved=0.0, food_waste_saved=0.0
        )
        db.add(p8)
        db.commit()
        
        b8_1 = models.Batch(
            product_id=p8.id, batch_number="MSR-B900", quantity=30, initial_quantity=50,
            manufacture_date=now - timedelta(days=380), expiry_date=now - timedelta(days=5), # Expired 5 days ago!
            cost_price=70.00, storage_location="Shelf C3", temperature_controlled=False, status="active"
        )
        db.add(b8_1)
        
        db.commit()

        # 4. Seed Sales History (Last 7 Days)
        sales = [
            # Day -6
            models.Sale(product_id=p1.id, quantity=3, unit_price=450.0, total_price=1350.0, timestamp=now - timedelta(days=6)),
            models.Sale(product_id=p3.id, quantity=12, unit_price=90.0, total_price=1080.0, timestamp=now - timedelta(days=6)),
            models.Sale(product_id=p7.id, quantity=5, unit_price=160.0, total_price=800.0, timestamp=now - timedelta(days=6)),
            # Day -5
            models.Sale(product_id=p2.id, quantity=8, unit_price=120.0, total_price=960.0, timestamp=now - timedelta(days=5)),
            models.Sale(product_id=p3.id, quantity=15, unit_price=90.0, total_price=1350.0, timestamp=now - timedelta(days=5)),
            models.Sale(product_id=p5.id, quantity=4, unit_price=320.0, total_price=1280.0, timestamp=now - timedelta(days=5)),
            # Day -4
            models.Sale(product_id=p1.id, quantity=5, unit_price=450.0, total_price=2250.0, timestamp=now - timedelta(days=4)),
            models.Sale(product_id=p4.id, quantity=6, unit_price=180.0, total_price=1080.0, timestamp=now - timedelta(days=4)),
            models.Sale(product_id=p6.id, quantity=10, unit_price=290.0, total_price=2900.0, timestamp=now - timedelta(days=4)),
            # Day -3
            models.Sale(product_id=p3.id, quantity=14, unit_price=90.0, total_price=1260.0, timestamp=now - timedelta(days=3)),
            models.Sale(product_id=p7.id, quantity=8, unit_price=160.0, total_price=1280.0, timestamp=now - timedelta(days=3)),
            # Day -2
            models.Sale(product_id=p2.id, quantity=12, unit_price=120.0, total_price=1440.0, timestamp=now - timedelta(days=2)),
            models.Sale(product_id=p5.id, quantity=6, unit_price=320.0, total_price=1920.0, timestamp=now - timedelta(days=2)),
            # Day -1
            models.Sale(product_id=p3.id, quantity=20, unit_price=90.0, total_price=1800.0, timestamp=now - timedelta(days=1)),
            models.Sale(product_id=p6.id, quantity=8, unit_price=290.0, total_price=2320.0, timestamp=now - timedelta(days=1)),
            models.Sale(product_id=p7.id, quantity=10, unit_price=160.0, total_price=1600.0, timestamp=now - timedelta(days=1)),
        ]
        for s in sales:
            db.add(s)
        db.commit()
        
        # 5. Run health check to initialize alerts and recommendations
        crud.run_inventory_health_check(db)
        
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
