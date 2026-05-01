"""Incident detection and correlation logic."""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import aiosqlite

INCIDENT_RULES = {
    "TAILGATING": {
        "description": "Two or more people entered on single badge swipe",
        "severity": "HIGH",
        "pattern": ["badge_read", "motion_detected"]
    },
    "DURESS_ALARM": {
        "description": "Duress code triggered",
        "severity": "CRITICAL",
        "pattern": ["duress_code"]
    },
    "FORCED_ENTRY": {
        "description": "Door forced open without valid credential",
        "severity": "CRITICAL",
        "pattern": ["door_forced", "door_opened"]
    },
    "REPEATED_DENIALS": {
        "description": "Multiple failed access attempts in short period",
        "severity": "HIGH",
        "pattern": ["access_denied"]
    },
    "UNAUTHORIZED_ACCESS": {
        "description": "Unknown identity attempted access",
        "severity": "HIGH",
        "pattern": ["invalid_credential"]
    },
    "AFTER_HOURS_INTRUSION": {
        "description": "Access detected outside operating hours",
        "severity": "HIGH",
        "pattern": ["access_allowed"]
    },
    "CAMERA_TAMPER": {
        "description": "Camera tampered or disconnected",
        "severity": "CRITICAL",
        "pattern": ["camera_tamper"]
    },
    "TEMPERATURE_CRITICAL": {
        "description": "Critical temperature detected in sensitive area",
        "severity": "HIGH",
        "pattern": ["temperature_alarm"]
    },
    "INTRUSION_TRIP": {
        "description": "Intrusion sensor triggered in restricted area",
        "severity": "CRITICAL",
        "pattern": ["intrusion_alarm"]
    }
}

async def detect_incidents(db: aiosqlite.Connection) -> List[Dict[str, Any]]:
    """Detect incidents from recent raw events."""
    incidents = []
    now = datetime.utcnow()
    lookback_minutes = 30  # Look at events from last 30 minutes
    
    # Get recent uncorrelated events
    cursor = await db.execute(
        """SELECT * FROM events_raw 
           WHERE created_at > datetime('now', '-' || ? || ' minutes')
           ORDER BY timestamp DESC""",
        (lookback_minutes,)
    )
    events = await cursor.fetchall()
    events = [dict(row) for row in events]
    
    if not events:
        return []
    
    # Check for tailgating pattern
    incidents.extend(await _detect_tailgating(db, events))
    
    # Check for duress
    incidents.extend(await _detect_duress(db, events))
    
    # Check for forced entry
    incidents.extend(await _detect_forced_entry(db, events))
    
    # Check for repeated denials
    incidents.extend(await _detect_repeated_denials(db, events))
    
    # Check for after-hours intrusion
    incidents.extend(await _detect_after_hours(db, events))
    
    # Save incidents to database
    for incident in incidents:
        # Check if already exists
        existing = await db.execute(
            "SELECT incident_id FROM incidents_correlated WHERE incident_id = ?",
            (incident['incident_id'],)
        )
        if not await existing.fetchone():
            await db.execute(
                """INSERT INTO incidents_correlated 
                   (incident_id, incident_type, severity, risk_score, location, 
                    building, person_id, person_name, description, event_ids, 
                    start_time, created_at, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    incident['incident_id'],
                    incident['type'],
                    incident['severity'],
                    incident['risk_score'],
                    incident['location'],
                    incident['building'],
                    incident.get('person_id', ''),
                    incident.get('person_name', ''),
                    incident['description'],
                    json.dumps(incident['event_ids']),
                    incident['timestamp'],
                    incident['created_at'],
                    'OPEN'
                )
            )
    
    await db.commit()
    return incidents

async def _detect_tailgating(db: aiosqlite.Connection, events: List[Dict]) -> List[Dict]:
    """Detect tailgating incidents."""
    incidents = []
    
    # Look for motion detection after badge read
    for i, event in enumerate(events):
        if 'badge' in event.get('event_name', '').lower():
            # Check for motion in next few seconds
            event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            for j in range(i+1, min(i+5, len(events))):
                next_event = events[j]
                if 'motion' in next_event.get('event_name', '').lower():
                    next_time = datetime.fromisoformat(next_event['timestamp'].replace('Z', '+00:00'))
                    if (next_time - event_time).total_seconds() < 10:
                        incidents.append({
                            'incident_id': f"tail_{event['event_id']}",
                            'type': 'TAILGATING',
                            'severity': 'HIGH',
                            'risk_score': 0.85,
                            'description': 'Multiple individuals detected entering on single badge swipe',
                            'location': event.get('location', 'Unknown'),
                            'building': event.get('building', 'Unknown'),
                            'person_id': event.get('person_id'),
                            'person_name': event.get('person_name'),
                            'event_ids': [event['event_id'], next_event['event_id']],
                            'timestamp': event['timestamp'],
                            'created_at': datetime.utcnow().isoformat() + 'Z'
                        })
                        break
    
    return incidents

async def _detect_duress(db: aiosqlite.Connection, events: List[Dict]) -> List[Dict]:
    """Detect duress incidents."""
    incidents = []
    
    for event in events:
        if 'duress' in event.get('event_name', '').lower():
            incidents.append({
                'incident_id': f"duress_{event['event_id']}",
                'type': 'DURESS_ALARM',
                'severity': 'CRITICAL',
                'risk_score': 0.99,
                'description': 'Duress code triggered - immediate response required',
                'location': event.get('location', 'Unknown'),
                'building': event.get('building', 'Unknown'),
                'person_id': event.get('person_id'),
                'person_name': event.get('person_name'),
                'event_ids': [event['event_id']],
                'timestamp': event['timestamp'],
                'created_at': datetime.utcnow().isoformat() + 'Z'
            })
    
    return incidents

async def _detect_forced_entry(db: aiosqlite.Connection, events: List[Dict]) -> List[Dict]:
    """Detect forced entry incidents."""
    incidents = []
    
    for event in events:
        if 'forced' in event.get('event_name', '').lower() or 'tamper' in event.get('event_name', '').lower():
            incidents.append({
                'incident_id': f"forced_{event['event_id']}",
                'type': 'FORCED_ENTRY',
                'severity': 'CRITICAL',
                'risk_score': 0.95,
                'description': 'Unauthorized entry detected - physical breach',
                'location': event.get('location', 'Unknown'),
                'building': event.get('building', 'Unknown'),
                'person_id': event.get('person_id'),
                'person_name': event.get('person_name'),
                'event_ids': [event['event_id']],
                'timestamp': event['timestamp'],
                'created_at': datetime.utcnow().isoformat() + 'Z'
            })
    
    return incidents

async def _detect_repeated_denials(db: aiosqlite.Connection, events: List[Dict]) -> List[Dict]:
    """Detect repeated access denials."""
    incidents = []
    
    # Group events by person and location in last 2 minutes
    event_map = {}
    for event in events:
        if 'denied' in event.get('event_name', '').lower() or 'denied' in event.get('message', '').lower():
            key = (event.get('person_id'), event.get('location'))
            if key not in event_map:
                event_map[key] = []
            event_map[key].append(event)
    
    for key, group in event_map.items():
        if len(group) >= 3:  # 3+ denials
            incidents.append({
                'incident_id': f"denial_{group[0]['event_id']}",
                'type': 'REPEATED_DENIALS',
                'severity': 'HIGH',
                'risk_score': 0.80,
                'description': f'{len(group)} failed access attempts detected - possible reconnaissance',
                'location': group[0].get('location', 'Unknown'),
                'building': group[0].get('building', 'Unknown'),
                'person_id': group[0].get('person_id'),
                'person_name': group[0].get('person_name'),
                'event_ids': [e['event_id'] for e in group],
                'timestamp': group[0]['timestamp'],
                'created_at': datetime.utcnow().isoformat() + 'Z'
            })
    
    return incidents

async def _detect_after_hours(db: aiosqlite.Connection, events: List[Dict]) -> List[Dict]:
    """Detect after-hours intrusions."""
    incidents = []
    
    for event in events:
        event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        hour = event_time.hour
        
        # Outside business hours (6 AM - 8 PM)
        if hour < 6 or hour > 20:
            if 'access' in event.get('event_name', '').lower() and 'allowed' in event.get('event_name', '').lower():
                incidents.append({
                    'incident_id': f"after_{event['event_id']}",
                    'type': 'AFTER_HOURS_INTRUSION',
                    'severity': 'HIGH',
                    'risk_score': 0.75,
                    'description': f'Access granted outside business hours at {event.get("location")}',
                    'location': event.get('location', 'Unknown'),
                    'building': event.get('building', 'Unknown'),
                    'person_id': event.get('person_id'),
                    'person_name': event.get('person_name'),
                    'event_ids': [event['event_id']],
                    'timestamp': event['timestamp'],
                    'created_at': datetime.utcnow().isoformat() + 'Z'
                })
    
    return incidents
