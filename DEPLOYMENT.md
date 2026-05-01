# 🚀 EventHorizon SOC - Hosting & Deployment Guide

This guide provides step-by-step instructions for hosting EventHorizon SOC on Railway or Heroku.

## ⚡ Quick Summary

**EventHorizon SOC** is a FastAPI-based Security Operations Center that:
- Streams simulated security events from COSEC (access control) and SATATYA (CCTV) systems
- Detects correlated security incidents (tailgating, duress, intrusions, etc.)
- Uses Google Gemini AI to generate human-readable security alerts
- Provides a real-time dashboard for SOC analysts

## 📋 Prerequisites

Before deploying, you'll need:

1. **Git** installed locally ([git-scm.com](https://git-scm.com))
2. **Code repository** on GitHub ([Sign up free](https://github.com))
3. **Google Gemini API key** ([Get free API key](https://ai.google.dev))
   - Sign up at Google AI Studio
   - Generate an API key
4. **Deployment platform account**:
   - **Railway**: [railway.app](https://railway.app) (recommended - simpler)
   - **Heroku**: [heroku.com](https://www.heroku.com)

## 🔧 Local Testing (Before Deploying)

### 1. Clone or initialize your repository

```bash
cd "c:\Users\Ayush Sarvaiya\Downloads\Event Horizon\EventHorizon"
git init
git add .
git commit -m "Initial EventHorizon SOC setup"
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# or: source venv/bin/activate  # On Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
# Copy the example file
copy .env.example .env  # Windows
# or: cp .env.example .env  # Mac/Linux

# Edit .env and add your Google Gemini API key
# GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Run locally

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: **http://localhost:8000**

You should see:
- ✅ Dashboard loads
- ✅ "Connected" health indicator
- ✅ "Start Stream" button works
- ✅ Events appear in the table
- ✅ "Analyze" button generates alerts

## 🚄 Deploy to Railway (Recommended)

Railway is the easiest option - no credit card required, generous free tier.

### Step 1: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/EventHorizon.git
git branch -M main
git push -u origin main
```

### Step 2: Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Click **Create New Project**
3. Select **Deploy from GitHub**
4. Authorize GitHub and select your `EventHorizon` repository
5. Railway auto-detects Python and starts building

### Step 3: Add environment variables

In Railway dashboard:
1. Go to **Variables**
2. Add these environment variables:
   ```
   GEMINI_API_KEY = your_google_api_key
   DATABASE_URL = eventhorizon.db
   PYTHONUNBUFFERED = 1
   ```

### Step 4: Deploy

Railway automatically deploys when you push to `main` branch.

Your app will be live at: `https://your-project.up.railway.app`

---

## 🎯 Deploy to Heroku

Alternative option if you prefer Heroku.

### Step 1: Create Heroku account & install CLI

1. Sign up at [heroku.com](https://www.heroku.com)
2. Download [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Login: `heroku login`

### Step 2: Create app and deploy

```bash
# Create a new Heroku app
heroku create your-app-name

# Add environment variables
heroku config:set GEMINI_API_KEY=your_google_api_key
heroku config:set DATABASE_URL=eventhorizon.db
heroku config:set PYTHONUNBUFFERED=1

# Deploy
git push heroku main
```

Your app will be live at: `https://your-app-name.herokuapp.com`

### Step 3: View logs

```bash
heroku logs --tail
```

---

## 🔑 Getting Your Google Gemini API Key

1. Go to [Google AI Studio](https://ai.google.dev)
2. Click **Get API Key**
3. Create a new API key
4. Copy the key and add it to your deployment platform

**Free tier**: 20 requests/day (enough for demos)
**Quota increases** once you add billing info

---

## 📊 Dashboard Usage

Once deployed:

### 1. Stream Events
- Click **"Start Stream"** to populate the event table
- Events are simulated from a 24-hour campus scenario
- Streams 200 events at 10x speed (takes ~2 minutes)

### 2. Detect Incidents
- Click **"Analyze"** to run incident correlation
- Detects: tailgating, duress, forced entry, access anomalies, etc.
- Incidents appear in the **Incidents** table

### 3. Generate Alerts
- AI analysis runs automatically every 15 seconds
- Alerts slide in as toasts (top-right)
- Click alert to see **full AI reasoning** + **raw events**
- Click **✕** to dismiss

---

## 🐛 Troubleshooting

### Issue: "Database locked" error
- SQLite limitations with high concurrency
- Fix: See [Production Database Setup](#production-database-setup) below

### Issue: Gemini API errors (429 - Rate Limited)
- You've hit the free tier quota
- Fix: Add billing info to Google Cloud Console for higher limits
- Or wait 24 hours for quota reset

### Issue: Dashboard shows "Error" health indicator
- Backend server crashed or not reachable
- Check logs:
  - **Railway**: Click **Logs** in dashboard
  - **Heroku**: Run `heroku logs --tail`

### Issue: No events in table after clicking "Start Stream"
- Check browser console for errors (F12)
- Verify API is responding: `curl https://your-app/health`

---

## 📦 Production Database Setup (Advanced)

For production deployments with high load, replace SQLite with PostgreSQL:

### 1. On Railway/Heroku, add PostgreSQL addon:

**Railway**:
- In Variables, set `DATABASE_URL` to the PostgreSQL connection string

**Heroku**:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### 2. Update `app/database.py`:

```python
# Change from:
DB_PATH = "eventhorizon.db"

# To:
import asyncpg
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///eventhorizon.db")

# Use asyncpg for PostgreSQL connections instead of aiosqlite
```

---

## 🔄 CI/CD & Auto-Deployment

Both Railway and Heroku support auto-deployment on git push:

```bash
# Make a change
echo "# Updated" >> README.md

# Push to GitHub
git add .
git commit -m "Update readme"
git push origin main

# Deployment happens automatically!
# Check status in Railway/Heroku dashboard
```

---

## 📈 Monitoring & Scaling

### View Application Metrics
- **Railway**: Metrics tab shows CPU, memory, requests
- **Heroku**: `heroku metrics`

### Scale up if needed
- **Railway**: Drag memory slider in dashboard
- **Heroku**: `heroku ps:scale web=2`

---

## 🎓 Next Steps

1. ✅ Deploy and get your app URL
2. ✅ Generate test data with **Start Stream** → **Analyze**
3. ✅ Customize incident detection in `app/incident_detector.py`
4. ✅ Modify AI prompts in `app/ai_analyzer.py`
5. ✅ Add custom event sources (COSEC/SATATYA APIs)
6. ✅ Integrate with your existing security systems

---

## 📚 Project Structure

```
EventHorizon/
├── app/
│   ├── main.py                 # FastAPI server
│   ├── database.py             # SQLite schema & queries
│   ├── incident_detector.py    # Incident detection logic
│   ├── ai_analyzer.py          # Google Gemini integration
│   ├── event_simulator.py      # Event generation
│   ├── static/
│   │   ├── app.js              # Dashboard logic
│   │   └── style.css           # Dashboard styling
│   └── templates/
│       └── index.html          # Dashboard UI
├── requirements.txt            # Python dependencies
├── Procfile                    # Heroku deployment
├── railway.toml               # Railway deployment
└── .env.example               # Environment template
```

---

## 💬 Support

- EventHorizon Documentation: `EventHorizon_Project_Documentation.md`
- FastAPI Docs: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- Railway Support: [docs.railway.app](https://docs.railway.app)
- Heroku Support: [devcenter.heroku.com](https://devcenter.heroku.com)

---

**Status**: ✅ Ready to deploy! Your EventHorizon SOC is fully configured and ready for hosting.
