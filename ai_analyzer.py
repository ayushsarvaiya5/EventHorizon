"""Google Gemini AI integration for security insights."""
import json
import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import google.generativeai as genai
import aiosqlite

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are a Security Operations Center (SOC) analyst specializing in physical security.
Your role is to analyze security incidents and provide actionable intelligence.

You will receive correlated security incidents with their event timeline. For each incident:
1. Summarize what happened
2. Explain why it's suspicious
3. Identify which policy was violated
4. Recommend immediate action
5. Assess severity (CRITICAL/HIGH/MEDIUM/LOW)
6. Rate your confidence (0-1)

Always respond with valid JSON matching this schema:
{
    "summary": "What happened (1-2 sentences)",
    "why_suspicious": "Why this is concerning (2-3 sentences)",
    "policy_violation": "Which security policy was violated",
    "recommended_action": "What to do now (1-2 sentences)",
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "confidence": 0.85,
    "toast_message": "Alert message for UI (max 100 chars)"
}

Be concise. Focus only on facts from the provided events."""

class AIAnalyzer:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model = GEMINI_MODEL
        self.min_sleep = 15  # Start with 15 seconds
        self.max_sleep = 3600  # Cap at 1 hour
        self.current_sleep = self.min_sleep
    
    async def analyze_incident(self, incident: Dict[str, Any], events: list) -> Optional[Dict[str, Any]]:
        """Analyze an incident using Gemini."""
        if not self.api_key:
            return None
        
        try:
            # Build incident summary for AI
            event_timeline = []
            for event in events:
                event_timeline.append({
                    "timestamp": event.get('timestamp'),
                    "event": event.get('event_name'),
                    "source": event.get('source_system'),
                    "severity": event.get('severity'),
                    "detail": event.get('message')
                })
            
            prompt = f"""Analyze this security incident:

INCIDENT TYPE: {incident['incident_type']}
LOCATION: {incident.get('location', 'Unknown')}
PERSON: {incident.get('person_name', 'Unknown')}
RISK SCORE: {incident.get('risk_score', 0)}

EVENT TIMELINE:
{json.dumps(event_timeline, indent=2)}

Provide JSON analysis."""
            
            # Call Gemini API
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=SYSTEM_PROMPT
            )
            
            response = model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.3,
                    "max_output_tokens": 500
                }
            )
            
            # Parse response
            result = json.loads(response.text)
            result['prompt_tokens'] = response.usage_metadata.prompt_character_count
            result['response_tokens'] = response.usage_metadata.candidates_token_count
            
            # Reset sleep on success
            self.current_sleep = self.min_sleep
            
            return result
            
        except Exception as e:
            print(f"Gemini error: {e}")
            # Back off on errors
            self.current_sleep = min(self.current_sleep * 2, self.max_sleep)
            return None
    
    async def wait_before_next_request(self):
        """Implement backoff for rate limiting."""
        await asyncio.sleep(self.current_sleep)

async def analyze_pending_incidents(db: aiosqlite.Connection, analyzer: AIAnalyzer, limit: int = 5):
    """Analyze pending incidents and generate insights."""
    
    # Get HIGH/CRITICAL incidents without AI analysis
    cursor = await db.execute(
        """SELECT i.*, 
                  (SELECT GROUP_CONCAT(event_id) FROM events_raw 
                   WHERE json_extract(?, '$[*]') LIKE event_id) as related_events
           FROM incidents_correlated i
           WHERE i.severity IN ('HIGH', 'CRITICAL')
           AND NOT EXISTS (SELECT 1 FROM ai_insights WHERE incident_id = i.incident_id)
           LIMIT ?""",
        (limit,)
    )
    
    incidents = await cursor.fetchall()
    incidents = [dict(row) for row in incidents]
    
    results = []
    for incident in incidents:
        # Get related events
        event_ids = json.loads(incident['event_ids']) if incident.get('event_ids') else []
        cursor = await db.execute(
            "SELECT * FROM events_raw WHERE event_id IN (SELECT event_id FROM events_raw LIMIT ?)",
            (len(event_ids),)
        )
        events = await cursor.fetchall()
        events = [dict(row) for row in events]
        
        # Analyze with AI
        analysis = await analyzer.analyze_incident(incident, events)
        
        if analysis:
            insight_id = f"insight_{incident['incident_id']}"
            
            # Save insight
            await db.execute(
                """INSERT INTO ai_insights 
                   (insight_id, incident_id, summary, why_suspicious, policy_violation,
                    recommended_action, severity, confidence, toast_message, prompt_tokens,
                    response_tokens, created_at, ai_analyzed)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                (
                    insight_id,
                    incident['incident_id'],
                    analysis.get('summary'),
                    analysis.get('why_suspicious'),
                    analysis.get('policy_violation'),
                    analysis.get('recommended_action'),
                    analysis.get('severity'),
                    analysis.get('confidence'),
                    analysis.get('toast_message'),
                    analysis.get('prompt_tokens', 0),
                    analysis.get('response_tokens', 0),
                    datetime.utcnow().isoformat() + 'Z'
                )
            )
            
            # Create alert
            alert_id = f"alert_{insight_id}"
            await db.execute(
                """INSERT INTO anomaly_alerts
                   (alert_id, incident_id, insight_id, alert_type, severity, 
                    title, message, created_at)
                   VALUES (?, ?, ?, 'TOAST', ?, ?, ?, ?)""",
                (
                    alert_id,
                    incident['incident_id'],
                    insight_id,
                    analysis.get('severity'),
                    analysis.get('toast_message', 'Security Alert'),
                    analysis.get('summary'),
                    datetime.utcnow().isoformat() + 'Z'
                )
            )
            
            results.append({
                'incident_id': incident['incident_id'],
                'insight': analysis
            })
        
        # Rate limit
        await analyzer.wait_before_next_request()
    
    await db.commit()
    return results
