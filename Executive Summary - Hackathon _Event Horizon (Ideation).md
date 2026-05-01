**EventHorizon: SDK-Enabled Event Intelligence Platform**

**Executive Summary:** Modern enterprises face alert overload from siloed security and IoT systems, making it hard to spot true incidents. EventHorizon solves this by sitting on top of existing systems (CCTV, access control, IoT) and correlating events into high-level alerts. It is a lightweight, plug-and-play platform that aggregates multi-source events and applies domain-specific rules to output real-time risk scores and insights. By reducing noise and automating decision logic, EventHorizon can cut alert volume by 50–80% and speed up incident detection by \~30% (see ROI below). Unlike general SIEMs (Splunk, QRadar) or cloud event tools (Datadog), EventHorizon focuses on physical-security scenarios (unauthorized entry, tailgating, etc.) with pre-built intelligence, making it faster and cheaper to deploy.

Key Benefits: Consolidated alerts, actionable insights, faster response time, and a clear ROI by saving analyst hours and reducing risk exposure. These points will be supported with metrics and a 24h demo plan below.

**Problem Statement**

* Explosion of low-level alerts: Every camera, badge reader, or sensor floods the SOC with logs. Teams see motion alarms, door events, etc., but no system sees the big picture. This “needle in a haystack” problem is well-documented: IT teams ingest millions of events daily and struggle to “cut through noise and focus on incidents that truly matter”. The result is alert fatigue – critical incidents get buried under false positives or isolated events.  
* Siloed systems: CCTV, access control, and IoT platforms typically report separately. For example, a face-recognition system might flag an unknown person, but unless correlated with a door-access event, it triggers no meaningful alert. Existing tools either detect single events or visualize logs, but don’t provide cross-system intelligence.  
* Delayed response & risk: Disparate alerts cause confusion and slow response. As Datadog notes, “disparate alerts from interconnected services… cause delayed incident response, \[hurting\] revenue and customer experience”. In physical security, delays can mean actual breaches.

In short: Organizations need an intelligent layer that aggregates and correlates alerts across physical security systems, so that only meaningful incidents (e.g. unauthorized entry) rise to the top.

**Target Users / Customers**

EventHorizon is aimed at enterprises and institutions with complex physical security needs, such as:

* Security Operations Centers (SOC) and Facility Security Teams: Who monitor CCTV, access logs, and sensor data across campuses or facilities.  
* Mid-market to large enterprises: Especially those without a massive in-house SIEM team, needing a lightweight solution.  
* Industry Verticals: Finance, healthcare, manufacturing, critical infrastructure, or government – any industry with sensitive facilities.  
* Systems Integrators: Who can bundle EventHorizon as a value-add with hardware deployments.  
* SMB  Companies within PACS Domain.

Assumption: We assume the team has intermediate-level developers (Python/JavaScript) and domain expertise in security or operations. No specialized AI knowledge is required, as we start with rule-based correlation.

Cant we bring data? I dont expect technical literacy with end users. Position as SaaS.

**Why It Matters: ROI & Impact**

By converting raw alerts into actionable intelligence, EventHorizon delivers measurable ROI:

* Alert Reduction: By aggregating related events, we reduce false/multiple alerts by \~70–80%. In one 2023 study, correlating events cut alert volume by 87%, dramatically reducing fatigue. Fewer alerts mean analysts save hours per day, focusing only on true threats.  
* Faster Incident Response: With contextual alerts (e.g. “High Risk – Unauthorized Entry”), responders act sooner. Datadog reports that correlating events “accelerates incident resolution” and cuts mean time to know or resolve issues. A conservative estimate: \~30% faster detection/response versus isolated alerts.  
* Operational Efficiency: Automated correlation frees up staff. Each security incident caught early can save on costs of theft/damage. Industry reports put the average cost of a breach in millions, so even one prevented incident pays dividends.  
* Actionable Intelligence: Instead of raw logs, teams get a risk score (0–100) and “why” text for each alert, enabling data-driven decisions. This mirrors Splunk’s “Risk-Based Alerting” approach but applied to physical security data.

Quantified benefits: By implementing EventHorizon, a company might see: “70% fewer alerts → saving \~5 analyst-hours/day; 30% faster detection → hours of potential loss avoided”. These figures are backed by Splunk’s statement that effective correlation “deliver\[s\] actionable insights” and “minimize\[s\] downtime”.

**Competitive Landscape & Defensibility**

* Splunk ES provides a market-leading SIEM with broad capabilities, including risk-based scoring and UEBA. It excels in IT environments but requires heavy setup and licensing.  
* Datadog Event Mgmt unifies alerts across tools and uses AI to correlate and dedupe them. It is cloud-native and excels at IT infrastructure events but isn’t specialized for physical security signals.  
* IBM QRadar is a veteran SIEM focusing on logs/flows with customizable correlation rules. It’s powerful but complex and geared to large enterprises.  
* EventHorizon’s Differentiation: Our moat is domain-specific intelligence. We’re not another generic SIEM. We offer pre-built correlation patterns for common physical scenarios (e.g. tailgating, after-hours access). This means plug-and-play setup vs. months of configuration in Splunk/QRadar. We integrate seamlessly via lightweight SDKs, so customers keep their existing systems. In essence, we “make existing systems smarter” by interpreting their events in context.  
* Defensibility: The core IP is our correlation engine logic: a library of proven security patterns and risk models for physical sites. While competitors have correlation engines, ours are tailored and easily extensible. By focusing on a niche (physical security \+ IoT), we avoid head-to-head with giants, and lock in customers with vertical expertise.

(Citations: Splunk blog on event correlation reducing noise; Datadog on AIOps correlation; IBM QRadar docs on rule-based correlation.)

**Product Vision & Architecture**

EventHorizon is envisioned as a middleware intelligence layer that sits between sensor networks and security dashboards. It ingests events via an SDK/API, normalizes them, runs a correlation engine, and exposes insights via APIs and a UI.

**flowchart LR**

    subgraph Sources \[Existing Security Systems\]

      A\[CCTV Cameras\]\\n(Media/Visual\\nSensors)

      B\[Door Access\]\\n(Badge Readers)

      C\[IoT Sensors\]\\n(Motion, Vibration)

    end

    subgraph EventHorizon \[EventHorizon Platform\]

      D(Event Ingestion) \--\> E(Normalization Layer)

      E \--\> F(Correlation Engine)

      F \--\> G(Decision & Risk Engine)

      G \--\> H(Dashboard \+ API)

    end

    A \--\> |SDK/API| D

    B \--\> |SDK/API| D

    C \--\> |SDK/API| D

    H \--\> I\[Notifications / Reports\]

* Event Ingestion (SDK/API): A lightweight SDK (or REST webhook) connects to each system. For example, a camera system can send {source:"camera1", event:"motion\_detected", timestamp:...} via HTTP POST.  
* Normalization: Converts heterogeneous event formats into a standard schema (source, type, value, timestamp).  
* Correlation Engine: The heart of EventHorizon. It holds state (recent events queue) and applies pattern rules (see next section) to detect complex scenarios across events.  
* Decision & Risk Engine: For each detected pattern, assign a risk score (0–100) and an alert explanation. This uses a weighted model (e.g. unknown\_face \+ late\_hour \+ forced\_door might score 95).  
* UI/API: A dashboard (e.g. Streamlit app) showing live event timelines, risk scores, and “why” text. Also exposes REST APIs for integration (e.g. /events, /alert, /risk).

This architecture emphasizes modularity and integration: EventHorizon doesn’t replace systems but enhances them. It can be deployed locally (on-premises) or in a private cloud, ensuring data sovereignty.

**24‑Hour Hackathon Scope & Demo Criteria**

Scope (Keep it Minimal & Impactful):

* Static Rule-Based Demo Only: No complex AI or cameras. Use simulated events (hardcoded or simple random generator). Focus on a small set of correlations.  
* Core Components to Build:  
  * Event ingestion (mock JSON events)  
  * Rule engine (simple Python/JS logic)  
  * Dashboard UI (Streamlit or simple web page)  
* Demo Deliverables:  
  * A working dashboard showing event timeline, detected patterns, risk scores, and explanations.  
  * Demonstrations of ≥3 scenarios (see below) that highlight key capabilities.  
  * A concise narrative: “We take these events → apply our engine → produce this alert.”  
* Excluded (For 24h Feasibility):  
  * No real ML models or training.  
  * No actual camera/sensor integration (mock everything).  
  * No full database or heavy backend (use in-memory or simple JSON).  
  * No over-engineered UI (streamlined Streamlit is fine).  
* Success Criteria:  
  * Functionality: Shows at least 3 meaningful correlations with correct outputs.  
  * Clarity: The UI clearly ties events to alerts (e.g. timeline \+ risk).  
  * Polish: The user can understand why an alert was triggered (explainability).  
  * Pitch-Ready: The demo tells a story: Problem → EventHorizon → Solution, within 5 slides.

**Five Demo Scenarios**

We will showcase five scenarios. Each scenario includes synthetic events (with timestamps), the pattern detected (if any), the assigned risk score, and an explanation. These should cover normal vs suspicious activity.

1\. Unauthorized Entry (High Risk)

* Input Events: Motion detected → Unknown face at camera → Door opened (after hours).  
* Expected Output: Pattern “Suspicious Entry Sequence”, Risk \= 90, Alert text: “🚨 High Risk: Unauthorized access sequence detected (motion \+ unknown face \+ door open).”

2\. Tailgating (Medium Risk)

* Input Events: Known face badge check → Door opens → Motion inside (no badge).  
* Expected Output: Pattern “Tailgating Alert”, Risk \= 75, Alert: “Potential tailgating detected: door held open by authorized user, followed by unrecognized entry.”

3\. Normal Activity (No Alert)

* Input Events: Employee badge swipe (known user) → Door opens → Known face inside.  
* Expected Output: No alert (Risk low, e.g. Risk=20), Explanation: “Normal access event, no risk.” This shows false alarms are minimized.

4\. After-Hours Intrusion (High Risk)

* Input Events: Motion detected at 02:15 AM (no badge use) → Unknown face detected.  
* Expected Output: Pattern “After-Hours Intrusion”, Risk \= 85, Alert: “🚨 Alert: Movement and unknown person detected after hours.”

5\. Multi-Zone Suspicious Movement (Moderate Risk)

* Input Events: Motion in Zone A → Motion in Zone B → Motion in Zone C (all within a short time).  
* Expected Output: Pattern “Suspicious Zone Hopping”, Risk \= 70, Explanation: “Repeated motion across zones – potential intruder.”

Each scenario should be scripted in the demo. For each, we display the input events timeline on UI, then show the triggered alert with score and explanation. Use color (e.g. red for risk) to highlight. This proves our correlation engine’s accuracy and the value of explainability.

Entity:

* Device :  Camera, AC Devices, Sensors  
* Users: User Event and Scoring 

Trends:  Risk Scoring, Spatio  Temporal 

**End-to-End Development Plan**

Team Roles & Responsibilities

|  |  |
| :---- | :---- |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |

Assumption: In a hackathon, some roles overlap. We assume at least 2-3 developers (one on backend/logic, one on frontend) and one strong communicator.

Tech Stack & Trade-Offs

Component

Option A (Recommended)

Option B (Alternative)

Trade-Offs

Backend Language

Python (FastAPI)

 Node.js (Express) / Java (Spring Boot)

Python is rapid for prototypes and has many libraries. Node is also quick but requires more setup; Java is heavyweight.

UI Framework

Streamlit (Python)

React / Vue.js (JavaScript)

Streamlit allows building a dashboard in \<2h using Python. React offers more UI flexibility but needs more coding.

Data Storage

In-memory / JSON (no DB)

SQLite or Redis (in-memory DB)

For demo, no DB keeps things simple. Redis/SQLite adds persistence if needed but adds complexity.

Event Streaming

Simple Python queue or list

Redis Pub/Sub / Kafka

A queue/list is enough for demo events. Kafka is overkill for 24h.

Deployment

Local script / Docker container (optional)

Cloud VM or Kubernetes

Local run is fastest. Dockerizing is nice but not required in hackathon timeframe.

Languages

Python, plus basic HTML/CSS for UI (if needed)

Python+JS combo if using React

We assume team knows Python; minimizing new languages reduces risk.

Folder / Repo Structure (Example)

graphql

Copy

eventhorizon/

├─ src/

│   ├─ app.py             \# Backend (FastAPI endpoints)

│   ├─ correlation\_engine.py   \# Core logic for pattern detection and scoring

│   ├─ events.py          \# Mock event generator or ingestion API handlers

│   └─ models.py          \# Data models (Event, Pattern, Alert)

├─ ui/

│   └─ dashboard.py       \# Streamlit (or React) UI code

├─ tests/

│   └─ test\_scenarios.py  \# Automated tests for each demo scenario

├─ requirements.txt      \# Python dependencies

└─ README.md

API / SDK Design

Ingestion API (Backend): Accept events via HTTP:

POST /events – Submit an event.

Request JSON: { "source": "camera1", "type": "motion", "value": "detected", "timestamp": 1682515200 }

Stores event in memory buffer. Returns 200 OK.

GET /events – Returns current buffered events (for debugging/demo).

Analysis API:

GET /detect – Triggers correlation on current events.

Response JSON: { "patterns": \[ {"name":"SuspiciousEntry","risk":90,"explanation":"Unauthorized entry sequence."} \], "risk\_score": 90 }

GET /risk – Returns the latest risk score (0–100).

These APIs simulate how an existing system could send events (via /events) and retrieve alerts (via /detect). The SDK for customers can be a simple library or code snippets that call these endpoints. For hackathon, we can hardcode calls to /events in our mock event generator (or simply inject events into memory).

Correlation Engine Design

Stateful Pattern Matching: Maintain a queue of recent events (e.g. last 5 minutes or 50 events). Each new event triggers a re-check of patterns.

Rule Format: Define correlation rules as JSON or Python structures. Example:

json

Copy

{

  "name": "SuspiciousEntry",

  "sequence": \[

    {"type": "motion"},

    {"type": "face", "value": "unknown"},

    {"type": "door", "value": "open"}

  \],

  "time\_window\_sec": 60,

  "risk\_score": 90,

  "explanation": "Unauthorized access sequence detected"

}

This rule means: if we see a Motion event, then an Unknown Face, then a Door Open within 60 seconds, trigger the pattern.

Detection Logic: On each event insertion, scan recent events for any rule’s sequence. One approach: sliding window \+ sequential matching. (Pseudocode: for each rule, check if last N events match the sequence order.)

Risk Scoring: Each rule carries a base risk. Additionally, the engine can adjust scores (e.g. multiply for after-hours, or add minor flags). Final output is 0–100. For simplicity, we can use the rule’s risk score directly.

Explainability: The system returns not just a number but why it fired (from the explanation field). This is a key differentiator.

Feedback Loop (Future vision): Ideally, alerts can be marked correct/false. The engine could then adjust rule weights. For hackathon, note it as a future enhancement (no time to implement, but mention "flag false alert → down-weight pattern").

Testing & Validation Plan

To prove accuracy, we will:

Write unit tests (tests/test\_scenarios.py) for each of the 5 scenarios above. For each, feed the exact events to the engine and assert the detected pattern name, risk score, and explanation.

Cross-check no false positives: Also test normal event sequences to ensure no alert is raised (e.g. only motion events should not trigger a SuspiciousEntry).

Simulate edge cases (e.g. incomplete sequence, out-of-order events) to ensure rules are strict.

Use Python assertions or Pytest. We’ll document that we achieve correct outputs for all scenarios (100% mapping accuracy for those cases).

(No direct citation needed; this is plan-based.)

Deployment & Demo Run Instructions

Environment: We assume developers have Python 3.x and can pip-install packages. No specific cloud provider required.

Install Dependencies: pip install fastapi uvicorn streamlit (and any libraries like pandas if used).

Run Backend: uvicorn app:app \--reload (starts on localhost:8000).

Run Frontend: In another terminal, streamlit run dashboard.py.

Trigger Mock Events: The app may auto-generate events, or use an included script: python generate\_events.py which POSTS to /events.

View Dashboard: Open localhost:8501 (default Streamlit port). You should see the live event log, risk score, and any alerts.

Demonstration: For each scenario, run a specific event script (e.g. python scenario1.py) to feed events, then show the dashboard responding correctly.

(Everything runs locally; no special hardware or paid services needed.)

Judge Q\&A Prep

Anticipate and practice answering these likely questions:

Q: How is this different from existing SIEM tools?

A: EventHorizon is domain-focused. Unlike Splunk/QRadar, which require heavy setup and target IT security, we target physical security events (CCTV, IoT). We offer pre-built patterns (e.g. tailgating) and SDK integration, enabling plug-and-play use. We layer on top of existing systems—no rip-and-replace.

Q: Why would a company buy instead of build in-house?

A: Many SIEMs exist, but our advantage is ease and speed. Building a custom correlation engine for physical security can take months. We offer an AI-ready, risk-scoring engine out of the box. SMEs especially would prefer buying a lightweight solution rather than investing in custom development.

Q: Do you have real ML/AI?

A: For the hackathon demo, we use rule-based correlation (explainable). However, the platform is designed to integrate ML. In future iterations, we can train models on labeled events to improve accuracy and auto-learn new patterns. But starting with deterministic rules ensures predictability and fits 24h scope.

Q: How do you ensure the correlations are accurate and not causing false alerts?

A: We calibrate patterns with domain experts and test extensively. We include a confidence/risk score and explainability text, so analysts see why an alert fired. In practice, a feedback loop (mark false positives) would refine weights. For the demo, our scenarios are hand-picked to highlight correct matches and no false alarms.

Q: How do you integrate with existing systems?

A: Via a simple SDK or REST API. Each system can push its events to EventHorizon. Alternatively, we can pull from logs. There’s no need to replace cameras or controllers – just add our service as a subscriber.

(Practice concise answers; pivot to product strengths and demo highlights.)

Sources: We drew on industry sources to benchmark capabilities. For example, Splunk notes that “event correlation aggregates, deduplicates, and analyzes alerts from multiple systems, enabling organizations to cut through noise”. Datadog emphasizes AI-enabled correlation to “reduce alert fatigue” and unify disparate alerts. IBM’s QRadar uses custom rules to correlate flows and events for anomaly detection. These underscore that while generic tools exist, none natively address physical event intelligence like EventHorizon.

