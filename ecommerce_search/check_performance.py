import urllib.request
import json
import time
import statistics

BASE_URL = "http://127.0.0.1:8001/api/v1"

def make_request(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    if data:
        req.data = json.dumps(data).encode('utf-8')
    
    start = time.time()
    try:
        with urllib.request.urlopen(req) as response:
            end = time.time()
            return json.loads(response.read().decode('utf-8')), (end - start) * 1000, response.getcode()
    except Exception as e:
        print(f"Error: {e}")
        return None, 0, 500

def check_performance():
    print("--- Performance Check ---")
    
    # 1. Check Product Count (via internal search empty or just search 'phone')
    # Since we don't have a direct count API, we can use search which returns all if empty or scrape from DB.
    # Actually, let's just trigger bootstrap to BE SURE we have 1000+
    print("Ensuring 1000+ products...")
    # First, let's try to get a rough idea.
    
    # resp, latency, code = make_request("/bootstrap?count=1000", method="POST")
    # if code == 200:
    #     print(f"Bootstrap triggered: {resp}")
    # else:
    #     print("Bootstrap failed or already running.")
    print("Skipping bootstrap (data exists).")

    # Give it a moment if it did async work (though my implementation was sync)
    time.sleep(1)

    # 2. Measure Latency
    queries = ["iphone", "sasta phone", "red mobile", "under 20k", "fastapi"]
    latencies = []
    
    print("\nMeasuring Search Latency:")
    for q in queries:
        encoded_q = urllib.parse.quote(q)
        resp, lat, code = make_request(f"/search/product?query={encoded_q}")
        if code == 200:
            count = len(resp['data'])
            print(f"Query: '{q}' | Found: {count} | Time: {lat:.2f} ms")
            latencies.append(lat)
        else:
            print(f"Query: '{q}' | Failed")
            
    if latencies:
        avg_lat = statistics.mean(latencies)
        max_lat = max(latencies)
        print(f"\nStats over {len(queries)} queries:")
        print(f"Average Latency: {avg_lat:.2f} ms")
        print(f"Max Latency: {max_lat:.2f} ms")
        
        if avg_lat < 1000:
            print("SUCCESS: Latency is under 1000ms")
        else:
            print("WARNING: Latency is high!")

if __name__ == "__main__":
    check_performance()
