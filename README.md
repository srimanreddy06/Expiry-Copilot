# Expiry Copilot — Enterprise Inventory Waste Intelligence Platform

Expiry Copilot is a next-generation, AI-powered inventory operations platform designed to help retail pharmacies, supermarkets, and healthcare facilities predict batch-level expirations, optimize markdown pricing, automate First-Expired-First-Out (FEFO) routing, and eliminate inventory waste.

---

## 🌟 About Expiry Copilot

Food, pharmaceutical, and chemical waste costs organizations billions of dollars annually while contributing significantly to global carbon emissions. Expiry Copilot bridges the gap between static inventory spreadsheets and proactive operations using Artificial Intelligence.

### Core Capabilities

1. **Dynamic Batch & FEFO Tracking**: Automatically maps batches to their storage node locations and deducts stock based on First-Expired-First-Out logic to maximize shelf life utilization.
2. **AI Clearance Markdown Engine**: Runs complex shelf-life degradation checks to recommend dynamic discount curves (e.g., 10%, 25%, 50% markdowns) as expiration approaches, optimizing cost recovery.
3. **OCR Invoicing Label Scanner**: Drag and drop consignment invoices or product box labels. The built-in AI extracts SKU, batch numbers, manufacture timestamps, and quantities in under 2 seconds.
4. **Interactive Chat Copilot & Text-to-SQL**: Converse in plain English with your AI assistant to query stock health, analyze trends, or translate natural language queries directly into raw database SQL commands.
5. **ML Demand Forecasting**: Computes customer purchasing behavior, seasonality patterns, and historical run rates to prevent stockout events and avoid over-ordering near-expiry batches.
6. **Carbon & ESG Green Tracking**: Calculates organic food volume and drug waste saved, converting it into auditable carbon offset data logs directly inside dashboard reports.

---

## 🛠️ Technology Stack

- **Frontend**: Next.js 16 (App Router), TypeScript, Tailwind CSS v4, Framer Motion, Recharts, Three.js (for the interactive `<FloatingLines />` canvas).
- **Backend**: FastAPI (Python), SQLAlchemy, SQLite, Uvicorn.
- **AI Integrations**: Gemini API (Google Generative AI), Google Cloud Vision OCR.
- **Authentication**: JWT tokens, Google OAuth 2.0.

---

## 🚀 Running the Project Locally

### Backend Setup
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the development server:
   ```bash
   python run.py
   ```

### Frontend Setup
1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## ☁️ Deployment

### Backend (Render)
The FastAPI server can be deployed to **Render** using the provided `render.yaml` Blueprint:
1. Connect your repository to Render.
2. Render will automatically parse the `render.yaml` specification.
3. Configure the following **Environment Variables** in the Render console:
   * `GOOGLE_CLIENT_ID`: Your Google OAuth Client ID.
   * `GOOGLE_CLIENT_SECRET`: Your Google OAuth Client Secret.
   * `GEMINI_API_KEY`: Your Google Gemini API Key.
4. Click **Apply** to deploy.

### Frontend (Vercel)
The Next.js client is optimized for deployment on **Vercel**:
1. Connect your repository to Vercel.
2. Select `frontend` as the **Root Directory**.
3. Set the following **Environment Variables** in Vercel Settings:
   * `NEXT_PUBLIC_API_URL`: Your live Render backend API URL (e.g., `https://expiry-copilot-backend.onrender.com/api/v1`).
   * `NEXT_PUBLIC_GOOGLE_CLIENT_ID`: Your Google OAuth Client ID (falls back to a default if not configured).
4. Click **Deploy**.
