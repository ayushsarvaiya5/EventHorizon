import urllib.request, urllib.parse, json, time

# Stream 6s at 300x to populate fresh incidents
print('--- Streaming events ---')
r = urllib.request.urlopen('http://127.0.0.1:8000/stream?start_date=2026-04-30T20:00:00&speed=300')
deadline = time.time() + 6
for line in r:
    if time.time() > deadline:
        break
r.close()
time.sleep(1)

# Trigger Gemini analysis
print('--- POST /api/ai/analyze ---')
req = urllib.request.Request('http://127.0.0.1:8000/api/ai/analyze?limit=5', method='POST')
r = urllib.request.urlopen(req, timeout=180)
result = json.loads(r.read())
print(json.dumps(result, indent=2))

# Show insights
print()
print('--- /api/ai/insights ---')
r = urllib.request.urlopen('http://127.0.0.1:8000/api/ai/insights?limit=5')
data = json.loads(r.read())
for ins in data['insights']:
    print()
    print('SUMMARY:        ', ins['summary'])
    print('WHY SUSPICIOUS: ', ins['why_suspicious'])
    print('POLICY:         ', ins['policy_violation'])
    print('ACTION:         ', ins['recommended_action'])
    print('TOAST:          ', ins['toast_message'])
    print('SEVERITY:       ', ins['severity'])
    print('TOKENS (in/out):', ins['prompt_tokens'], '/', ins['response_tokens'])

# Show alerts
print()
print('--- /api/alerts/pending ---')
r = urllib.request.urlopen('http://127.0.0.1:8000/api/alerts/pending')
alerts = json.loads(r.read())
print('Pending alerts:', alerts['count'])
for a in alerts['alerts'][:5]:
    print('  [' + a['severity'] + '] ' + a['title'] + ': ' + a['message'])
