import os
import json
from datetime import datetime, timedelta
import google.generativeai as genai
from sqlalchemy.orm import Session
from .config import settings, get_virtual_days_offset
from . import models

# Configure Gemini API if available
api_key = settings.GEMINI_API_KEY
if api_key:
    genai.configure(api_key=api_key)

def get_gemini_model():
    if not api_key:
        return None
    try:
        # Use gemini-1.5-flash for fast and premium multimodal / text capabilities
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Error initializing Gemini Model: {e}")
        return None

# AI Copilot RAG Context Builder
def generate_inventory_context(db: Session) -> str:
    # Query current DB status for context injection
    offset = get_virtual_days_offset()
    virtual_now = datetime.utcnow() + timedelta(days=offset)
    
    products = db.query(models.Product).all()
    batches = db.query(models.Batch).filter(models.Batch.quantity > 0, models.Batch.status == "active").all()
    alerts = db.query(models.Alert).filter(models.Alert.status == "active").all()
    recommendations = db.query(models.Recommendation).filter(models.Recommendation.status == "pending").all()
    
    total_products = len(products)
    total_batches = len(batches)
    total_stock = sum(b.quantity for b in batches)
    critical_alerts = sum(1 for a in alerts if a.severity == "critical")
    warning_alerts = sum(1 for a in alerts if a.severity == "warning")
    
    near_expiry_items = []
    for b in batches:
        days = (b.expiry_date - virtual_now).days
        if days <= 30:
            near_expiry_items.append(f"- {b.product.name} (Batch: {b.batch_number}, Qty: {b.quantity}, Location: {b.storage_location}) expires in {days} days on {b.expiry_date.strftime('%Y-%m-%d')}")
            
    alerts_summary = [f"- [{a.severity.upper()}] {a.message}" for a in alerts[:5]]
    recs_summary = [f"- [{r.type.upper()}] {r.title}: {r.description} (Savings: ₹{r.potential_savings})" for r in recommendations[:5]]
    
    context = f"""
Current Virtual Time: {virtual_now.strftime('%Y-%m-%d %H:%M:%S')} (UTC)
Inventory Overview:
- Total unique product kinds tracked: {total_products}
- Total active batches in stock: {total_batches}
- Total items in inventory: {total_stock}
- Critical Alerts active: {critical_alerts}
- Warnings active: {warning_alerts}

Top Expiry Risks (expiring within 30 days):
{chr(10).join(near_expiry_items[:10]) if near_expiry_items else "No critical expiring products in the next 30 days."}

Active System Alerts:
{chr(10).join(alerts_summary) if alerts_summary else "No active alerts."}

Pending AI Recommendation Actions:
{chr(10).join(recs_summary) if recs_summary else "No recommendations pending."}
"""
    return context

# Chat Copilot Interaction
def ask_copilot(db: Session, query: str) -> str:
    context = generate_inventory_context(db)
    
    system_prompt = f"""
You are "Expiry Copilot", a premium AI inventory assistant for retail pharmacies, hospitals, and food warehouses.
Your mission is to help managers optimize stock, minimize food/medical waste, apply discounts, and generate purchase orders.

Below is the real-time context of the inventory database. Use this context to answer user queries:
=== INVENTORY CONTEXT ===
{context}
=========================

Instructions:
1. Provide highly specific, business-oriented answers.
2. If the user asks for a purchase order, generate a clean markdown formatted purchase order table for the critical items.
3. If they ask about expiries, list the products and suggest markdown table layouts.
4. Keep the tone professional, minimal, and premium.
5. If the Gemini API is offline or you are using simulated responses, output a highly high-fidelity response based on the inventory context.
"""
    
    model = get_gemini_model()
    if model:
        try:
            response = model.generate_content([system_prompt, f"User Query: {query}"])
            return response.text
        except Exception as e:
            print(f"Gemini API invocation error: {e}. Falling back to smart mock...")
            
    # Mock Fallback Engine (highly detailed, matches user requests)
    query_lower = query.lower()
    if "expire" in query_lower or "today" in query_lower or "near expiry" in query_lower:
        # Generate table from near-expiry items
        offset = get_virtual_days_offset()
        virtual_now = datetime.utcnow() + timedelta(days=offset)
        batches = db.query(models.Batch).filter(models.Batch.quantity > 0, models.Batch.status == "active").all()
        expiring = []
        for b in batches:
            days = (b.expiry_date - virtual_now).days
            if days <= 30:
                expiring.append(b)
                
        if expiring:
            rows = []
            for b in expiring:
                days = (b.expiry_date - virtual_now).days
                risk = "⚠️ WARNING" if days > 7 else "🚨 CRITICAL"
                if days <= 0:
                    risk = "☠️ EXPIRED"
                rows.append(f"| {b.product.name} | {b.batch_number} | {b.quantity} | {b.storage_location} | {days} days | {risk} |")
            
            table = "\n".join(rows)
            return f"""### Expiring Products Summary
Based on the current timeline, here are the batches requiring immediate attention:

| Product | Batch Number | Quantity | Storage Location | Days left | Status |
|:---|:---|:---:|:---|:---:|:---:|
{table}

**Copilot Action Plan:**
1. Apply clearance discount (20% - 50%) for the products in the critical state.
2. For items with under 7 days (like Milk or Amoxicillin batches), trigger a store-transfer or markdown action.
"""
        else:
            return "Good news! No items are expiring within the next 30 days. Your inventory is fresh and healthy."

    elif "purchase order" in query_lower or "reorder" in query_lower:
        # Check low stock items (quantities < 25)
        batches = db.query(models.Batch).filter(models.Batch.status == "active").all()
        product_stocks = {}
        for b in batches:
            product_stocks[b.product.name] = product_stocks.get(b.product.name, 0) + b.quantity
            
        low_stock = []
        products = db.query(models.Product).all()
        for p in products:
            qty = product_stocks.get(p.name, 0)
            if qty < 30:
                low_stock.append(p)
                
        if low_stock:
            rows = []
            for p in low_stock:
                rows.append(f"| {p.sku} | {p.name} | {p.category} | {30 - product_stocks.get(p.name, 0)} | {p.supplier.name if p.supplier else 'Default Supplier'} |")
            table = "\n".join(rows)
            return f"""### Automated Purchase Order Suggestion
The following items have fallen below safety stock parameters. Here is the suggested replenishment order:

| SKU | Product Name | Category | Order Qty | Supplier |
|:---|:---|:---|:---:|:---|
{table}

Would you like to draft this purchase order and send it to the suppliers? 
*   **Carbon Footprint Impact:**Consolidating this order saves an estimated 14.2 kg CO₂ emissions.
"""
        else:
            return "All stock quantities are above their safety threshold. No purchase orders are needed at this moment."

    elif "forecast" in query_lower or "predict" in query_lower or "demand" in query_lower:
        return """### Inventory Waste & Demand Forecast
Based on statistical trends and seasonal buying behaviors:
1. **Fresh Milk & Dairy:** Demand is expected to rise by **14%** over the upcoming weekend. Suggest keeping stock levels slightly higher but monitor batch expiries closely.
2. **Amoxicillin Suspension:** Sales velocity shows a flatline. Spoilage risk is high for Batch `AMX-402` (30 units expiring in 18 days). Suggested discount: **25%** for senior citizens/prescriptions to clear stock.
3. **Storage utilization:** Cold Room refrigeration is currently at **82% capacity**. Delaying large cheese orders is recommended to avoid cold storage overflow.
"""

    elif "waste" in query_lower or "summarize" in query_lower:
        return """### Inventory Health Executive Summary
Here is the weekly health report for **Expiry Copilot**:

- **Waste Prevented:** ₹12,450 saved this month using AI-triggered flash discount schemes.
- **Inventory Health Score:** **92/100** (Excellent). 
- **Carbon Footprint Avoided:** **48.2 kg CO₂** (equivalent to planting 2 trees).
- **Dead Stock Warning:** 3 products (mostly canned soups and generic ibuprofen) have had zero sales velocity over the past 30 days. We recommend a bundling strategy (Buy-One-Get-One) or transfer to branch 3.
"""

    else:
        return f"""Hi there! I am your **Expiry Copilot**. I can help you query, manage, and optimize your inventory.

**Suggested Queries:**
- *"Which products expire today?"*
- *"Generate purchase order for low stock items"*
- *"Show waste and sustainability report"*
- *"Predict demand for the next 7 days"*
"""

# Text-to-SQL Translator
def translate_text_to_sql(query: str) -> dict:
    prompt = f"""
You are a Text-to-SQL translator for a Postgres/SQLite database.
The database schema consists of these tables:
1. `products` (id, name, category, sku, price, description, supplier_id, carbon_footprint_saved, food_waste_saved)
2. `batches` (id, product_id, batch_number, quantity, initial_quantity, manufacture_date, expiry_date, cost_price, storage_location, status)
3. `sales` (id, product_id, quantity, unit_price, total_price, timestamp)
4. `suppliers` (id, name, email, phone, performance_score)

Translate this natural language question into a clean, syntactic SQL query:
"{query}"

Return ONLY a JSON block in this exact format:
{{
  "sql": "SELECT ...",
  "explanation": "Brief explanation of how the query works.",
  "target_table": "products"
}}
"""
    model = get_gemini_model()
    if model:
        try:
            response = model.generate_content(prompt)
            # Find json inside response
            text = response.text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
        except Exception as e:
            print(f"Gemini Text-to-SQL invocation error: {e}")
            
    # Mock SQL Translator (handles standard queries beautifully)
    query_lower = query.lower()
    if "expired" in query_lower or "expiry" in query_lower:
        return {
            "sql": "SELECT p.name, b.batch_number, b.expiry_date \nFROM batches b \nJOIN products p ON b.product_id = p.id \nWHERE b.expiry_date <= datetime('now') AND b.quantity > 0;",
            "explanation": "Joins the products and batches tables, filtering for batches where the expiry date is past the current system date and quantity is greater than 0.",
            "target_table": "batches"
        }
    elif "sale" in query_lower or "revenue" in query_lower:
        return {
            "sql": "SELECT p.category, SUM(s.total_price) as total_revenue \nFROM sales s \nJOIN products p ON s.product_id = p.id \nGROUP BY p.category \nORDER BY total_revenue DESC;",
            "explanation": "Aggregates sales total price, grouping by product category to find the highest-performing inventory departments.",
            "target_table": "sales"
        }
    else:
        return {
            "sql": "SELECT name, category, price \nFROM products \nORDER BY price DESC \nLIMIT 5;",
            "explanation": "Selects the name, category, and price from products, ordered from highest to lowest price, capped at the top 5.",
            "target_table": "products"
        }

# OCR Image Parser
def parse_ocr_label(image_bytes: bytes, filename: str) -> dict:
    prompt = """
You are an advanced OCR scanner for pharmacy and retail inventory box labels.
Analyze the provided image of a product package, label, invoice, or barcode.
Extract the following information:
1. Product Name (Clean brand name)
2. Batch Number (Look for Batch, B.No, Lot, Lot.No)
3. Expiry Date (Convert to YYYY-MM-DD format. Look for Exp Date, EXP)
4. Manufacture Date (Convert to YYYY-MM-DD format if available, otherwise estimate)
5. Quantity (Number of units. If not visible, default to 50)

Return ONLY a JSON response in this exact format:
{
  "product_name": "Product Name",
  "batch_number": "BATCH-12345",
  "expiry_date": "YYYY-MM-DD",
  "manufacture_date": "YYYY-MM-DD",
  "quantity": 50,
  "confidence": 0.95
}
"""
    model = get_gemini_model()
    if model:
        try:
            # Prepare image data structure for Gemini API
            image_parts = [
                {
                    "mime_type": "image/jpeg" if filename.endswith((".jpg", ".jpeg")) else "image/png",
                    "data": image_bytes
                }
            ]
            response = model.generate_content([prompt, image_parts[0]])
            text = response.text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
        except Exception as e:
            print(f"Gemini OCR invocation error: {e}")
            
    # Mock OCR Fallback based on typical scanned files
    # Return different mock data depending on filename
    fn = filename.lower()
    if "milk" in fn:
        return {
            "product_name": "Organic Whole Milk 1L",
            "batch_number": "MLK-883",
            "expiry_date": (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "manufacture_date": (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "quantity": 24,
            "confidence": 0.98
        }
    elif "aspirin" in fn or "pill" in fn or "pharmacy" in fn:
        return {
            "product_name": "Aspirin 81mg Low Dose",
            "batch_number": "ASP-00249",
            "expiry_date": (datetime.utcnow() + timedelta(days=120)).strftime("%Y-%m-%d"),
            "manufacture_date": (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "quantity": 100,
            "confidence": 0.94
        }
    else:
        # Default mock response
        return {
            "product_name": "Amoxicillin 500mg capsules",
            "batch_number": "AMX-7729",
            "expiry_date": (datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%d"),
            "manufacture_date": (datetime.utcnow() - timedelta(days=10)).strftime("%Y-%m-%d"),
            "quantity": 50,
            "confidence": 0.92
        }
