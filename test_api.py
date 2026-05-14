import requests
import json

url = 'http://localhost:8000/v1/agent/chat'
payload = {'prompt': 'danh sách khách hàng'}

print('Testing with longer timeout...')
response = requests.post(url, json=payload, timeout=120)  # 2 minutes
print(f'Status: {response.status_code}')

if response.status_code == 200:
    result = response.json()
    execution = result.get('execution_state', {})
    print(f'Execution Status: {execution.get("status")}')
    if execution.get('status') == 'success':
        tasks = execution.get('tasks', [])
        if tasks and 'result' in tasks[0]:
            rows = tasks[0]['result'].get('rows', [])
            print(f'✅ Got {len(rows)} customers successfully')
            for i, row in enumerate(rows[:2]):
                print(f'  {i+1}. {row.get("name", "N/A")} - {row.get("industry", "N/A")}')
    else:
        print(f'❌ Execution failed: {execution.get("error", "Unknown")}')
else:
    print(f'❌ HTTP {response.status_code}: {response.text[:200]}')