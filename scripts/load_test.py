import requests
import concurrent.futures
import time

API_URL = "http://localhost:8000/v1/agent/chat"

def simulate_user_request(user_id: int):
    payload = {
        "prompt": f"Show me top 5 accounts for user {user_id}",
        "session_id": f"tenant_{user_id}",
        "thread_id": f"thread_{user_id}_{int(time.time())}"
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        return response.status_code
    except Exception as e:
        return str(e)

def run_load_test(num_users: int = 10):
    print(f"Starting load test with {num_users} concurrent users...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        results = list(executor.map(simulate_user_request, range(num_users)))
        
    end_time = time.time()
    
    successes = results.count(200)
    failures = len(results) - successes
    
    print(f"--- Load Test Results ---")
    print(f"Total Time: {end_time - start_time:.2f} seconds")
    print(f"Successful Requests: {successes}")
    print(f"Failed Requests: {failures}")
    print(f"Raw Results: {results}")

if __name__ == "__main__":
    run_load_test(10)
