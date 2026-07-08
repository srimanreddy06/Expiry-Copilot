# Expiry Copilot

Expiry Copilot is an Enterprise Inventory Waste Intelligence Platform designed to monitor and manage product expiry dates, optimize pricing strategies, and reduce food/medical waste.

## Project Structure

- **`backend/`**: FastAPI python server.
- **`frontend/`**: Next.js App Router client dashboard.

## Running the Project

### Backend
1. Go to the `backend` directory.
2. Run `.\.venv\Scripts\python run.py`.

### Frontend
1. Go to the `frontend` directory.
2. Run `npm run dev`.

## Deployment

### Backend (Render)
You can deploy the FastAPI backend on **Render** using the provided `render.yaml` blueprint:
1. Connect your GitHub repository to Render.
2. Render will automatically detect the `render.yaml` Blueprint.
3. Set your environment variables in the Render console (e.g., `GOOGLE_API_KEY` for AI features).
4. Click **Apply** to deploy.

Alternatively, to set it up manually:
- **Environment**: Python
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
The frontend is optimized for **Vercel**:
1. Connect your repository to Vercel.
2. Set the framework preset to **Next.js**.
3. Set `frontend` as the **Root Directory**.
4. Set the environment variable `NEXT_PUBLIC_API_URL` to point to your Render backend URL (e.g., `https://expiry-copilot-backend.onrender.com/api/v1`).
5. Deploy.

