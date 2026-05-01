"""Security event simulator based on Matrix COSEC and SATATYA events."""
import random
import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Matrix COSEC event codes (Access Control)
COSEC_EVENTS = [
    {"code": "2001", "name": "User Allowed", "severity": "LOW", "source": "COSEC"},
    {"code": "2002", "name": "Access Denied", "severity": "MEDIUM", "source": "COSEC"},
    {"code": "2003", "name": "User Duress", "severity": "CRITICAL", "source": "COSEC"},
    {"code": "2004", "name": "Door Forced", "severity": "CRITICAL", "source": "COSEC"},
    {"code": "2005", "name": "Door Tamper", "severity": "HIGH", "source": "COSEC"},
    {"code": "2006", "name": "Invalid Credential", "severity": "HIGH", "source": "COSEC"},
    {"code": "2007", "name": "Reader Communication Error", "severity": "MEDIUM", "source": "COSEC"},
    {"code": "2008", "name": "Reader Tamper", "severity": "HIGH", "source": "COSEC"},
]

# Matrix SATATYA event types (CCTV/Video)
SATATYA_EVENTS = [
    {"code": "3001", "name": "Motion Detected", "severity": "MEDIUM", "source": "SATATYA"},
    {"code": "3002", "name": "Motion Alarm", "severity": "HIGH", "source": "SATATYA"},
    {"code": "3003", "name": "Intrusion Detected", "severity": "CRITICAL", "source": "SATATYA"},
    {"code": "3004", "name": "Camera Tamper", "severity": "CRITICAL", "source": "SATATYA"},
    {"code": "3005", "name": "Camera Offline", "severity": "HIGH", "source": "SATATYA"},
    {"code": "3006", "name": "Video Loss", "severity": "HIGH", "source": "SATATYA"},
    {"code": "3007", "name": "Region Crossover", "severity": "MEDIUM", "source": "SATATYA"},
    {"code": "3008", "name": "Temperature Alarm", "severity": "HIGH", "source": "SATATYA"},
]

# Devices
DEVICES = {
    "COSEC": [
        {"id": "DOOR_001", "name": "Main Entrance", "location": "Ground Floor", "building": "A"},
        {"id": "DOOR_002", "name": "Server Room", "location": "Basement", "building": "A"},
        {"id": "DOOR_003", "name": "Executive Floor", "location": "10th Floor", "building": "A"},
        {"id": "DOOR_004", "name": "Lab Access", "location": "5th Floor", "building": "B"},
        {"id": "DOOR_005", "name": "HR Department", "location": "3rd Floor", "building": "B"},
        {"id": "READER_001", "name": "Badge Reader 1", "location": "Lobby", "building": "A"},
        {"id": "READER_002", "name": "Badge Reader 2", "location": "Elevator", "building": "A"},
    ],
    "SATATYA": [
        {"id": "CAM_001", "name": "Lobby Cam", "location": "Main Lobby", "building": "A"},
        {"id": "CAM_002", "name": "Server Cam", "location": "Server Room", "building": "A"},
        {"id": "CAM_003", "name": "Parking Cam", "location": "Parking B1", "building": "A"},
        {"id": "CAM_004", "name": "Lab Cam", "location": "Lab", "building": "B"},
        {"id": "CAM_005", "name": "Entrance Cam", "location": "Main Entrance", "building": "A"},
    ]
}

PEOPLE = [
    {"id": "P001", "name": "Vikram Mehta"},
    {"id": "P002", "name": "Sarah Chen"},
    {"id": "P003", "name": "Rajesh Patel"},
    {"id": "P004", "name": "Ananya Sharma"},
    {"id": "P005", "name": "Mohammed Hassan"},
    {"id": "P006", "name": "Lisa Anderson"},
    {"id": "P007", "name": "Unknown Intruder"},
]

# Correlation scenarios
SCENARIOS = [
    {
        "name": "Normal Access",
        "weight": 0.5,
        "events": [
            {"type": "COSEC", "index": 0, "delay": 0},  # User Allowed
        ]
    },
    {
        "name": "Tailgating",
        "weight": 0.15,
        "events": [
            {"type": "COSEC", "index": 0, "delay": 0},  # User Allowed
            {"type": "SATATYA", "index": 0, "delay": 2},  # Motion Detected
            {"type": "SATATYA", "index": 0, "delay": 3},  # Motion Detected
        ]
    },
    {
        "name": "Duress",
        "weight": 0.05,
        "events": [
            {"type": "COSEC", "index": 2, "delay": 0},  # User Duress
        ]
    },
    {
        "name": "Forced Entry",
        "weight": 0.05,
        "events": [
            {"type": "COSEC", "index": 3, "delay": 0},  # Door Forced
            {"type": "SATATYA", "index": 2, "delay": 1},  # Intrusion Detected
        ]
    },
    {
        "name": "Access Denied",
        "weight": 0.10,
        "events": [
            {"type": "COSEC", "index": 1, "delay": 0},  # Access Denied
            {"type": "COSEC", "index": 1, "delay": 5},  # Access Denied
            {"type": "COSEC", "index": 1, "delay": 10},  # Access Denied
        ]
    },
    {
        "name": "Camera Alarm",
        "weight": 0.08,
        "events": [
            {"type": "SATATYA", "index": 1, "delay": 0},  # Motion Alarm
            {"type": "SATATYA", "index": 2, "delay": 2},  # Intrusion Detected
        ]
    },
    {
        "name": "Equipment Tamper",
        "weight": 0.07,
        "events": [
            {"type": "COSEC", "index": 4, "delay": 0},  # Door Tamper
            {"type": "COSEC", "index": 7, "delay": 1},  # Reader Tamper
        ]
    },
]

class EventSimulator:
    def __init__(self):
        self.correlation_id = None
    
    def _get_time_weight(self, hour: int) -> float:
        """Get scenario weight multiplier based on time of day."""
        if 6 <= hour < 8:  # Morning rush
            return {"Normal Access": 1.5, "Tailgating": 2.0}
        elif 8 <= hour < 18:  # Business hours
            return {"Normal Access": 1.0, "Tailgating": 0.8}
        elif 18 <= hour < 20:  # Evening rush
            return {"Normal Access": 1.2, "Tailgating": 1.5}
        elif 20 <= hour < 24 or hour < 6:  # Night
            return {"After Hours": 2.0, "Intrusion": 3.0, "Forced Entry": 2.5}
        return {}
    
    def generate_events(self, start_time: datetime, count: int = 100, speed: int = 1) -> List[Dict[str, Any]]:
        """Generate simulated events."""
        events = []
        current_time = start_time
        
        for _ in range(count):
            # Select scenario based on weights and time
            hour = current_time.hour
            time_weights = self._get_time_weight(hour)
            
            scenario = random.choices(
                SCENARIOS,
                weights=[s["weight"] * time_weights.get(s["name"], 1.0) for s in SCENARIOS],
                k=1
            )[0]
            
            # Generate correlation
            correlation_id = str(uuid.uuid4())
            
            for event_spec in scenario["events"]:
                if event_spec["type"] == "COSEC":
                    event_list = COSEC_EVENTS
                    devices = DEVICES["COSEC"]
                else:
                    event_list = SATATYA_EVENTS
                    devices = DEVICES["SATATYA"]
                
                event_template = event_list[event_spec["index"]]
                device = random.choice(devices)
                person = random.choice(PEOPLE)
                
                event_time = current_time + timedelta(seconds=event_spec["delay"])
                
                event = {
                    "event_id": str(uuid.uuid4()),
                    "correlation_id": correlation_id,
                    "timestamp": event_time.isoformat() + "Z",
                    "source_system": event_template["source"],
                    "device_id": device["id"],
                    "device_name": device["name"],
                    "event_code": event_template["code"],
                    "event_name": event_template["name"],
                    "severity": event_template["severity"],
                    "message": f"{event_template['name']} at {device['name']}",
                    "person_id": person["id"],
                    "person_name": person["name"],
                    "location": device["location"],
                    "building": device["building"],
                    "details": {
                        "scenario": scenario["name"],
                        "device_type": "COSEC" if event_spec["type"] == "COSEC" else "CCTV",
                    }
                }
                
                events.append(event)
            
            # Move time forward (with speed multiplier)
            current_time += timedelta(seconds=random.randint(5, 30) / speed)
        
        return events
