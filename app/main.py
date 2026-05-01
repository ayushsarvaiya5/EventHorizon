"""FastAPI application for EventHorizon SOC."""
import asyncio
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import aiosqlite

from app.database import init_db, get_db, get_alert_by_id, get_alert_events, dismiss_alert
from app.incident_detector import detect_incidents
from app.ai_analyzer import AIAnalyzer, analyze_pending_incidents
from app.event_simulator import EventSimulator

# Global state
ai_analyzer = AIAnalyzer()
simulator = EventSimulator()
db_connection = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    # Startup
    print("🚀 Starting EventHorizon SOC...")
    await init_db()
    print("✅ Database initialized")
    
    # Start background tasks
    app.state.analysis_task = asyncio.create_task(background_analysis_loop())
    print("✅ Background analysis started")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    if hasattr(app.state, 'analysis_task'):
        app.state.analysis_task.cancel()

# Create FastAPI app
app = FastAPI(
    title="EventHorizon SOC",
    description="Security Operations Center for physical security events",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("app/static", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ============= Event Streaming =============

@app.get("/stream")
async def stream_events(
    start_date: str = "2026-04-30T20:00:00",
    speed: int = 1,
    count: int = 100
):
    """Stream simulated security events as Server-Sent Events."""
    
    async def generate():
        db = await get_db()
        
        start_time = datetime.fromisoformat(start_date)
        events = simulator.generate_events(start_time, count, speed)
        
        for event in events:
            # Insert into database
            await db.execute(
                """INSERT INTO events_raw 
                   (event_id, correlation_id, timestamp, source_system, device_id, 
                    device_name, event_code, event_name, severity, message, 
                    person_id, person_name, location, building, details, raw_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event['event_id'],
                    event['correlation_id'],
                    event['timestamp'],
                    event['source_system'],
                    event['device_id'],
                    event['device_name'],
                    event['event_code'],
                    event['event_name'],
                    event['severity'],
                    event['message'],
                    event['person_id'],
                    event['person_name'],
                    event['location'],
                    event['building'],
                    json.dumps(event['details']),
                    json.dumps(event),
                    datetime.utcnow().isoformat() + 'Z'
                )
            )
            
            yield f"data: {json.dumps(event)}\n\n"
        
        await db.commit()
        await db.close()
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# ============= API Endpoints =============

@app.get("/api/alerts/pending")
async def get_pending_alerts(limit: int = Query(10, ge=1, le=100)):
    """Get pending (undismissed) alerts."""
    db = await get_db()
    
    cursor = await db.execute(
        """SELECT * FROM anomaly_alerts 
           WHERE dismissed = 0 
           ORDER BY created_at DESC 
           LIMIT ?""",
        (limit,)
    )
    
    alerts = await cursor.fetchall()
    await db.close()
    
    return {
        "count": len(alerts),
        "alerts": [dict(alert) for alert in alerts]
    }

@app.get("/api/alerts/{alert_id}")
async def get_alert_detail(alert_id: str):
    """Get alert details with related events."""
    alert = await get_alert_by_id(alert_id)
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db = await get_db()
    
    # Get incident
    incident_cursor = await db.execute(
        "SELECT * FROM incidents_correlated WHERE incident_id = ?",
        (alert['incident_id'],)
    )
    incident = await incident_cursor.fetchone()
    
    # Get insight
    insight_cursor = await db.execute(
        "SELECT * FROM ai_insights WHERE insight_id = ?",
        (alert['insight_id'],)
    )
    insight = await insight_cursor.fetchone()
    
    # Get events
    event_ids = json.loads(incident['event_ids']) if incident else []
    if event_ids:
        placeholders = ','.join('?' * len(event_ids))
        events_cursor = await db.execute(
            f"SELECT * FROM events_raw WHERE event_id IN ({placeholders})",
            event_ids
        )
        events = await events_cursor.fetchall()
    else:
        events = []
    
    await db.close()
    
    return {
        "alert": dict(alert),
        "incident": dict(incident) if incident else None,
        "insight": dict(insight) if insight else None,
        "events": [dict(e) for e in events]
    }

@app.post("/api/alerts/{alert_id}/dismiss")
async def dismiss_alert_endpoint(alert_id: str):
    """Dismiss an alert."""
    success = await dismiss_alert(alert_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to dismiss alert")
    
    return {"status": "dismissed"}

@app.get("/api/incidents")
async def get_incidents(
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500)
):
    """Get recent incidents."""
    db = await get_db()
    
    query = "SELECT * FROM incidents_correlated"
    params = []
    
    if severity:
        query += " WHERE severity = ?"
        params.append(severity)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor = await db.execute(query, params)
    incidents = await cursor.fetchall()
    await db.close()
    
    return {
        "count": len(incidents),
        "incidents": [dict(inc) for inc in incidents]
    }

@app.get("/api/ai/insights")
async def get_ai_insights(
    limit: int = Query(20, ge=1, le=100)
):
    """Get AI-generated insights."""
    db = await get_db()
    
    cursor = await db.execute(
        """SELECT * FROM ai_insights 
           WHERE ai_analyzed = 1 
           ORDER BY created_at DESC 
           LIMIT ?""",
        (limit,)
    )
    
    insights = await cursor.fetchall()
    await db.close()
    
    return {
        "count": len(insights),
        "insights": [dict(ins) for ins in insights]
    }

@app.post("/api/ai/analyze")
async def trigger_ai_analysis(
    limit: int = Query(5, ge=1, le=20),
    background_tasks: BackgroundTasks = None
):
    """Trigger AI analysis of pending incidents."""
    db = await get_db()
    
    results = await analyze_pending_incidents(db, ai_analyzer, limit)
    
    await db.close()
    
    return {
        "analyzed": len(results),
        "results": results
    }

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics."""
    db = await get_db()
    
    # Count events
    events_cursor = await db.execute("SELECT COUNT(*) as count FROM events_raw")
    events_count = (await events_cursor.fetchone())['count']
    
    # Count incidents by severity
    critical_cursor = await db.execute(
        "SELECT COUNT(*) as count FROM incidents_correlated WHERE severity = 'CRITICAL'"
    )
    critical_count = (await critical_cursor.fetchone())['count']
    
    high_cursor = await db.execute(
        "SELECT COUNT(*) as count FROM incidents_correlated WHERE severity = 'HIGH'"
    )
    high_count = (await high_cursor.fetchone())['count']
    
    # Count pending alerts
    alerts_cursor = await db.execute(
        "SELECT COUNT(*) as count FROM anomaly_alerts WHERE dismissed = 0"
    )
    alerts_count = (await alerts_cursor.fetchone())['count']
    
    await db.close()
    
    return {
        "total_events": events_count,
        "critical_incidents": critical_count,
        "high_incidents": high_count,
        "pending_alerts": alerts_count,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }

@app.get("/")
async def index():
    """Serve dashboard."""
    return FileResponse("app/templates/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + 'Z'}

# ============= Background Tasks =============

async def background_analysis_loop():
    """Continuously analyze incidents in the background."""
    
    while True:
        try:
            await asyncio.sleep(15)  # Analyze every 15 seconds
            
            db = await get_db()
            
            # Detect new incidents from recent events
            await detect_incidents(db)
            
            # Analyze incidents with AI (if API key present)
            if os.getenv("GEMINI_API_KEY"):
                await analyze_pending_incidents(db, ai_analyzer, limit=5)
            
            await db.close()
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Background analysis error: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
