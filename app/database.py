"""Database setup and models for EventHorizon SOC."""
import sqlite3
import os
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
import aiosqlite
from datetime import datetime

DB_PATH = os.getenv("DATABASE_URL", "eventhorizon.db")

async def get_db():
    """Get database connection."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
    """Initialize database schema."""
    db = await get_db()
    
    await db.executescript("""
        -- Events raw data
        CREATE TABLE IF NOT EXISTS events_raw (
            event_id TEXT PRIMARY KEY,
            correlation_id TEXT,
            timestamp TEXT NOT NULL,
            source_system TEXT,
            device_id TEXT,
            device_name TEXT,
            event_code TEXT,
            event_name TEXT,
            severity TEXT,
            message TEXT,
            person_id TEXT,
            person_name TEXT,
            location TEXT,
            building TEXT,
            details TEXT,
            raw_json TEXT,
            created_at TEXT NOT NULL
        );
        
        -- Correlated incidents
        CREATE TABLE IF NOT EXISTS incidents_correlated (
            incident_id TEXT PRIMARY KEY,
            incident_type TEXT,
            severity TEXT,
            risk_score REAL,
            location TEXT,
            building TEXT,
            person_id TEXT,
            person_name TEXT,
            description TEXT,
            event_ids TEXT,
            start_time TEXT,
            end_time TEXT,
            created_at TEXT,
            updated_at TEXT,
            status TEXT DEFAULT 'OPEN'
        );
        
        -- AI insights
        CREATE TABLE IF NOT EXISTS ai_insights (
            insight_id TEXT PRIMARY KEY,
            incident_id TEXT,
            summary TEXT,
            why_suspicious TEXT,
            policy_violation TEXT,
            recommended_action TEXT,
            severity TEXT,
            confidence REAL,
            toast_message TEXT,
            prompt_tokens INTEGER,
            response_tokens INTEGER,
            created_at TEXT,
            ai_analyzed INTEGER DEFAULT 0,
            FOREIGN KEY (incident_id) REFERENCES incidents_correlated(incident_id)
        );
        
        -- Anomaly alerts (toasts)
        CREATE TABLE IF NOT EXISTS anomaly_alerts (
            alert_id TEXT PRIMARY KEY,
            incident_id TEXT,
            insight_id TEXT,
            alert_type TEXT,
            severity TEXT,
            title TEXT,
            message TEXT,
            dismissed INTEGER DEFAULT 0,
            created_at TEXT,
            dismissed_at TEXT,
            FOREIGN KEY (incident_id) REFERENCES incidents_correlated(incident_id),
            FOREIGN KEY (insight_id) REFERENCES ai_insights(insight_id)
        );
        
        -- Event stream state
        CREATE TABLE IF NOT EXISTS stream_state (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events_raw(timestamp);
        CREATE INDEX IF NOT EXISTS idx_events_correlation ON events_raw(correlation_id);
        CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents_correlated(severity);
        CREATE INDEX IF NOT EXISTS idx_alerts_dismissed ON anomaly_alerts(dismissed);
    """)
    
    await db.commit()
    await db.close()

async def get_alert_by_id(alert_id: str) -> Optional[Dict[str, Any]]:
    """Get alert with related events."""
    db = await get_db()
    alert = await db.execute(
        "SELECT * FROM anomaly_alerts WHERE alert_id = ?",
        (alert_id,)
    )
    alert_row = await alert.fetchone()
    await db.close()
    
    if not alert_row:
        return None
    
    return dict(alert_row)

async def get_alert_events(incident_id: str) -> List[Dict[str, Any]]:
    """Get all events for an incident."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM events_raw WHERE correlation_id IN (SELECT correlation_id FROM events_raw WHERE event_id IN (SELECT event_ids FROM incidents_correlated WHERE incident_id = ?)) ORDER BY timestamp",
        (incident_id,)
    )
    events = await cursor.fetchall()
    await db.close()
    
    return [dict(row) for row in events]

async def dismiss_alert(alert_id: str) -> bool:
    """Dismiss an alert."""
    db = await get_db()
    await db.execute(
        "UPDATE anomaly_alerts SET dismissed = 1, dismissed_at = ? WHERE alert_id = ?",
        (datetime.utcnow().isoformat() + "Z", alert_id)
    )
    await db.commit()
    await db.close()
    return True
