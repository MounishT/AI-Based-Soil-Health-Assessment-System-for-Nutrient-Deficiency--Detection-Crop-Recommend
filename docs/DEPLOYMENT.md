# Deployment Guide (Minimal Setup)

This guide walks you through deploying your AI Soil Health Monitor to the cloud for your mentor demo, using free and simple hosting platforms.

## 1. Backend Deployment (Render / Railway)

We recommend **Render.com** as it is free and natively supports Python/FastAPI.

### Steps for Render:
1. **Push your code to GitHub** (Ensure all your recent changes are pushed).
2. Go to [Render.com](https://render.com) and sign in with GitHub.
3. Click **New +** and select **Web Service**.
4. Connect your GitHub repository.
5. Configuration:
   - **Name**: `soil-health-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port 10000`
6. Click **Create Web Service**.

> [!IMPORTANT]
> Render's free tier spins down after 15 minutes of inactivity. When you show your mentor, it might take 30-50 seconds for the first API request to wake the server up.

---

## 2. Frontend Deployment (Vercel)

Vercel is the creator of Next.js and provides the absolute best deployment experience.

### Steps for Vercel:
1. Go to [Vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository.
4. **Configuration**:
   - Vercel will automatically detect that it's a Next.js project.
   - Expand **Build and Output Settings**.
   - Ensure the Root Directory is set to `frontend/` (if Vercel asks, or you can leave it as default if it auto-detects).
5. **Environment Variables**:
   - (Optional) If you want to use a `.env` file to point to your live Render API, you can add it here. For the demo, `page.js` is currently pointing to `http://127.0.0.1:8000` for local testing. 
   - *Note: Before deploying to Vercel, change `http://127.0.0.1:8000` in `frontend/app/page.js` to your new Render URL!*
6. Click **Deploy**.

## 3. PWA (Progressive Web App) Verification

Because we used `next-pwa`, once deployed to Vercel, you can open the URL on your mobile phone (Chrome/Safari) and you will see a prompt to **"Add to Home Screen"**. This will install the app like a native mobile app!
