import requests
import json

def test_api_connectivity():
    print("--- Running Phase 1 Test: API Connectivity ---")
    url = "http://localhost:5000/v1/agent/chat"
    payload = {"query": "Test kết nối"}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response JSON:")
            print(json.dumps(data, indent=2))
            
            # Check for trace logs
            if "trace_log" in data:
                print("PASS: Trace logs found in response.")
            else:
                print("FAIL: No trace logs in response.")
                
            if "answer" in data:
                print("PASS: Answer found in response.")
            else:
                print("FAIL: No answer in response.")
        else:
            print(f"FAIL: Unexpected status code {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Could not connect to API: {e}")

if __name__ == "__main__":
    test_api_connectivity()
