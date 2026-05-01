/* EventHorizon SOC Dashboard Application */

class DashboardApp {
    constructor() {
        this.baseUrl = window.location.origin;
        this.eventSource = null;
        this.updateInterval = null;
        this.events = [];
        this.alerts = [];
        this.incidents = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startHealthCheck();
        this.startStatsPolling();
        this.startAlertsPolling();
    }

    setupEventListeners() {
        document.getElementById('startStreamBtn').addEventListener('click', () => this.startEventStream());
        document.getElementById('analyzeBtn').addEventListener('click', () => this.triggerAnalysis());
    }

    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            if (response.ok) {
                document.getElementById('healthIndicator').textContent = '● Connected';
                document.getElementById('healthIndicator').classList.remove('error');
                return true;
            }
        } catch (error) {
            document.getElementById('healthIndicator').textContent = '● Error';
            document.getElementById('healthIndicator').classList.add('error');
        }
        return false;
    }

    startHealthCheck() {
        this.healthCheck();
        setInterval(() => this.healthCheck(), 10000);
    }

    startStatsPolling() {
        const updateStats = async () => {
            try {
                const response = await fetch(`${this.baseUrl}/api/stats`);
                const data = await response.json();
                
                document.getElementById('eventCount').textContent = data.total_events.toLocaleString();
                document.getElementById('criticalCount').textContent = data.critical_incidents;
                document.getElementById('highCount').textContent = data.high_incidents;
                document.getElementById('alertCount').textContent = data.pending_alerts;
            } catch (error) {
                console.error('Stats error:', error);
            }
        };

        updateStats();
        setInterval(updateStats, 5000);
    }

    startAlertsPolling() {
        const pollAlerts = async () => {
            try {
                const response = await fetch(`${this.baseUrl}/api/alerts/pending?limit=50`);
                const data = await response.json();
                this.displayAlerts(data.alerts);
            } catch (error) {
                console.error('Alerts error:', error);
            }
        };

        pollAlerts();
        setInterval(pollAlerts, 4000);
    }

    displayAlerts(alerts) {
        const container = document.getElementById('toastContainer');
        
        if (alerts.length === 0) {
            container.innerHTML = '<div class="no-alerts">No active alerts</div>';
            return;
        }

        // Group by dismissed status
        const undismissed = alerts.filter(a => !a.dismissed);
        
        if (undismissed.length === 0) {
            container.innerHTML = '<div class="no-alerts">All alerts dismissed</div>';
            return;
        }

        container.innerHTML = undismissed.map(alert => `
            <div class="toast ${alert.severity.toLowerCase()}" onclick="app.showAlertDetail('${alert.alert_id}')">
                <div class="toast-content">
                    <div class="toast-title">[${alert.severity}] ${alert.title}</div>
                    <div class="toast-message">${alert.message}</div>
                </div>
                <button class="toast-close" onclick="event.stopPropagation(); app.dismissAlert('${alert.alert_id}')">✕</button>
            </div>
        `).join('');
    }

    async dismissAlert(alertId) {
        try {
            await fetch(`${this.baseUrl}/api/alerts/${alertId}/dismiss`, { method: 'POST' });
            this.startAlertsPolling(); // Refresh alerts
        } catch (error) {
            console.error('Dismiss error:', error);
        }
    }

    async showAlertDetail(alertId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/alerts/${alertId}`);
            const data = await response.json();
            
            const modal = document.getElementById('alertModal');
            const body = document.getElementById('modalBody');
            
            let html = `
                <div class="detail-section">
                    <div class="detail-label">Alert</div>
                    <div class="detail-value">
                        <strong>[${data.alert.severity}]</strong> ${data.alert.title}
                    </div>
                </div>
            `;

            if (data.insight) {
                html += `
                    <div class="detail-section">
                        <div class="detail-label">AI Analysis</div>
                        <div class="detail-value">
                            <strong>Summary:</strong> ${data.insight.summary}<br><br>
                            <strong>Why Suspicious:</strong> ${data.insight.why_suspicious}<br><br>
                            <strong>Policy Violation:</strong> ${data.insight.policy_violation}<br><br>
                            <strong>Recommended Action:</strong> ${data.insight.recommended_action}<br><br>
                            <strong>Confidence:</strong> ${(data.insight.confidence * 100).toFixed(0)}%
                        </div>
                    </div>
                `;
            }

            if (data.incident) {
                html += `
                    <div class="detail-section">
                        <div class="detail-label">Incident Details</div>
                        <div class="detail-value">
                            <strong>Type:</strong> ${data.incident.incident_type}<br>
                            <strong>Location:</strong> ${data.incident.location}<br>
                            <strong>Person:</strong> ${data.incident.person_name}<br>
                            <strong>Risk Score:</strong> ${(data.incident.risk_score * 100).toFixed(0)}%
                        </div>
                    </div>
                `;
            }

            if (data.events && data.events.length > 0) {
                html += '<div class="detail-section"><div class="detail-label">Related Events</div>';
                data.events.forEach(event => {
                    html += `
                        <div class="detail-value" style="font-size: 11px; margin-bottom: 8px;">
                            <strong>${event.timestamp}</strong> - ${event.event_name} at ${event.location}
                            <span class="severity ${event.severity.toLowerCase()}">${event.severity}</span>
                        </div>
                    `;
                });
                html += '</div>';
            }

            body.innerHTML = html;
            modal.classList.add('active');
        } catch (error) {
            console.error('Detail error:', error);
        }
    }

    startEventStream() {
        const btn = document.getElementById('startStreamBtn');
        btn.disabled = true;
        btn.textContent = 'Streaming...';

        const now = new Date();
        const startTime = new Date(now.getTime() - 60 * 60 * 1000); // 1 hour ago
        const startDate = startTime.toISOString().split('Z')[0];

        if (this.eventSource) {
            this.eventSource.close();
        }

        this.eventSource = new EventSource(`${this.baseUrl}/stream?start_date=${startDate}&speed=10&count=200`);
        let eventCount = 0;

        this.eventSource.onmessage = (event) => {
            try {
                const eventData = JSON.parse(event.data);
                this.events.unshift(eventData);
                
                // Keep only recent events
                if (this.events.length > 500) {
                    this.events = this.events.slice(0, 500);
                }
                
                this.updateEventsTable();
                eventCount++;
            } catch (error) {
                console.error('Parse error:', error);
            }
        };

        this.eventSource.onerror = () => {
            this.eventSource.close();
            btn.disabled = false;
            btn.textContent = 'Start Stream';
            console.log('Stream ended. Streamed', eventCount, 'events');
        };
    }

    updateEventsTable() {
        const tbody = document.getElementById('eventsTableBody');
        const rows = this.events.slice(0, 50).map(event => `
            <tr>
                <td>${new Date(event.timestamp).toLocaleTimeString()}</td>
                <td>${event.event_name}</td>
                <td>${event.source_system}</td>
                <td>${event.location}</td>
                <td>${event.person_name}</td>
                <td><span class="severity ${event.severity.toLowerCase()}">${event.severity}</span></td>
            </tr>
        `);

        if (rows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6">No events yet</td></tr>';
        } else {
            tbody.innerHTML = rows.join('');
        }
    }

    async triggerAnalysis() {
        const btn = document.getElementById('analyzeBtn');
        btn.disabled = true;
        btn.textContent = 'Analyzing...';

        try {
            const response = await fetch(`${this.baseUrl}/api/ai/analyze?limit=10`, { method: 'POST' });
            const data = await response.json();
            
            console.log('Analysis complete:', data.analyzed, 'incidents analyzed');
            
            // Refresh incidents and alerts
            await this.refreshIncidents();
            this.startAlertsPolling();
        } catch (error) {
            console.error('Analysis error:', error);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Analyze';
        }
    }

    async refreshIncidents() {
        try {
            const response = await fetch(`${this.baseUrl}/api/incidents?limit=20`);
            const data = await response.json();
            this.displayIncidents(data.incidents);
        } catch (error) {
            console.error('Incidents error:', error);
        }
    }

    displayIncidents(incidents) {
        const tbody = document.getElementById('incidentsTableBody');
        
        if (incidents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6">No incidents</td></tr>';
            return;
        }

        const rows = incidents.slice(0, 20).map(incident => `
            <tr>
                <td>${incident.incident_type}</td>
                <td>${incident.location}</td>
                <td>${incident.person_name || '-'}</td>
                <td><span class="severity ${incident.severity.toLowerCase()}">${incident.severity}</span></td>
                <td>${(incident.risk_score * 100).toFixed(0)}%</td>
                <td>${incident.status}</td>
            </tr>
        `);

        tbody.innerHTML = rows.join('');
    }
}

function closeModal() {
    document.getElementById('alertModal').classList.remove('active');
}

// Initialize app when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new DashboardApp();
});
