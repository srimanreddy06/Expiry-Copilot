# 🚀 Expiry Copilot - Vercel Deployment Guide

This guide provides step-by-step instructions for deploying both the **Next.js Frontend** and the **FastAPI Backend** to Vercel (or other cloud platforms).

---

## 🏗️ Deployment Architectures

Because the backend relies on heavy libraries (Pandas, Gemini AI, SQLAlchemy) and is stateful (SQLite database by default), you have two primary deployment architectures:

### Option A: Separate Vercel Projects (Recommended for Free Tier)
Deploy both the frontend and backend on Vercel as two separate projects:
* **Frontend**: Next.js (Zero-config deployment)
* **Backend**: FastAPI (Python Serverless Function)

> [!IMPORTANT]
> Since Vercel Serverless Functions have an ephemeral (read-only) filesystem, using the default SQLite (`expiry_copilot.db`) on Vercel means any user modifications (like registering new users, adding transactions, or dismissing alerts) will be lost when the function spins down.
> 
> **To solve this**, connect to a hosted PostgreSQL instance (like **Neon**, **Supabase**, or **Vercel Postgres**) by setting the `DATABASE_URL` environment variable. The SQLAlchemy backend will automatically run migrations and seed database tables on the first startup.

### Option B: Frontend on Vercel & Backend on Persistent Host (Highly Recommended for Production)
Deploy the Next.js frontend on Vercel, and the FastAPI backend on a platform that supports persistent servers:
* **Backend Hosts**: [Render](https://render.com/), [Railway](https://railway.app/), or [Fly.io](https://fly.io/)
* **Benefits**: 
  - No cold starts (API is always responsive).
  - Can safely use SQLite on a persistent disk (no external Postgres needed).

---

## 🛠️ Step 1: Set Up a Hosted Database (Optional but Recommended)

If you are deploying the backend to Vercel (Option A), you will need a PostgreSQL database to persist changes:

1. Create a free account at [Neon Console](https://neon.tech/) or [Supabase](https://supabase.com/).
2. Create a new PostgreSQL database named `expiry_copilot`.
3. Copy the **Connection String** (URI format), which looks like:
   `postgresql://user:password@hostname/dbname?sslmode=require`
4. Keep this connection string handy as you will use it as the `DATABASE_URL` environment variable.

---

## 📦 Step 2: Deploy the Backend to Vercel

1. Log in to your [Vercel Dashboard](https://vercel.com/) and click **Add New** > **Project**.
2. Import the Git repository containing this code.
3. Configure the Project Settings:
   * **Project Name**: `expiry-copilot-backend`
   * **Framework Preset**: `Other`
   * **Root Directory**: `backend` (Click Edit, choose the `backend` folder, and click Continue).
4. Expand the **Environment Variables** section and add the following keys:
   * `DATABASE_URL`: Set this to your PostgreSQL connection string (if using Neon/Supabase). If left blank, Vercel will fall back to an ephemeral SQLite database.
   * `GEMINI_API_KEY`: Paste your Google Gemini API Key.
   * `SECRET_KEY`: Generate a random secure key for JWT tokens (e.g., `openssl rand -hex 32` or any random long string).
5. Click **Deploy**. Vercel will automatically build the serverless functions inside the `api/` directory using Python.
6. Once deployed, copy the generated **Production URL** (e.g., `https://expiry-copilot-backend.vercel.app`).

---

## 💻 Step 3: Deploy the Frontend to Vercel

1. Go back to your [Vercel Dashboard](https://vercel.com/) and click **Add New** > **Project**.
2. Import the *same* Git repository again.
3. Configure the Project Settings:
   * **Project Name**: `expiry-copilot`
   * **Framework Preset**: `Next.js`
   * **Root Directory**: `frontend` (Click Edit, choose the `frontend` folder, and click Continue).
4. Expand the **Environment Variables** section and add:
   * `NEXT_PUBLIC_API_URL`: Set this to the backend production URL you copied in Step 2 with the path `/api/v1` appended (e.g., `https://expiry-copilot-backend.vercel.app/api/v1`).
5. Click **Deploy**. Vercel will build the static pages and API routes for your Next.js application.

Your fullstack application is now successfully deployed! 🎉

---

## 🔍 Verification & Testing

To verify that your deployments are running successfully:
1. Open the frontend Vercel URL in your browser.
2. If you see the login page, try logging in with the seeded manager credentials:
   * **Username**: `admin`
   * **Password**: `admin123`
3. Inspect the browser console or network tab to ensure fetch requests are hitting the `NEXT_PUBLIC_API_URL` successfully.
4. Try uploading a label image to test the OCR AI integration and chat with the AI Copilot.
