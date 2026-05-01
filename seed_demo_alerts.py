"""Seed a few demo toast alerts for UI testing (used when Gemini quota is exhausted)."""
import sqlite3, uuid, datetime as dt

DB = "d:/HACKATHON/eventhorizon.db"
now = dt.datetime.utcnow().isoformat() + "Z"

demos = [
    ("CRITICAL", "DURESS ALARM",
     "Vikram Mehta triggered duress code at HR Department. Dispatch immediately."),
    ("CRITICAL", "Forced Entry",
     "Door forced open at Server Room without valid credential. Lockdown initiated."),
    ("HIGH",     "Tailgating Detected",
     "Two persons entered Executive Floor on a single badge swipe. Review CCTV."),
    ("HIGH",     "Repeated Access Denials",
     "5 failed access attempts at Data Center in 90s — possible reconnaissance."),
    ("HIGH",     "Unauthorized Access Attempt",
     "Unknown identity attempted access at Parking B1 Gate."),
]

c = sqlite3.connect(DB)
inserted = 0
for sev, title, msg in demos:
    aid = str(uuid.uuid4())
    c.execute(
        """INSERT INTO anomaly_alerts
           (alert_id, incident_id, insight_id, alert_type, severity, title, message, created_at)
           VALUES (?, '', '', 'TOAST', ?, ?, ?, ?)""",
        (aid, sev, title, msg, now),
    )
    inserted += 1
c.commit()
c.close()
print(f"Inserted {inserted} demo alerts.")
