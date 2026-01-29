import urllib.request
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8001/api/v1"

def make_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    
    if data:
        req.data = json.dumps(data).encode('utf-8')
        
    start = time.time()
    try:
        with urllib.request.urlopen(req) as response:
            duration = (time.time() - start) * 1000
            return json.loads(response.read().decode('utf-8')), response.getcode(), duration
    except Exception as e:
        duration = (time.time() - start) * 1000
        print(f"FAILED {endpoint}: {e}")
        return None, 500, duration

def run_suite():
    print("=== FINAL SYSTEM HEALTH CHECK ===")
    
    tests = []
    
    # 1. Product Management
    product_id = 0
    print("\n[1/6] Testing Product Management...")
    new_prod = {
        "title": "Test Phone 2026", "description": "Verification unit", "mrp": 1000, "price": 900, "stock": 10, "rating": 5.0
    }
    resp, code, dur = make_request("POST", "/product", new_prod)
    if code == 201:
        product_id = resp['productId']
        tests.append(("POST /product", "PASS", f"{dur:.2f}ms"))
    else:
        tests.append(("POST /product", "FAIL", f"{dur:.2f}ms"))
        
    if product_id:
        update_data = {"productId": product_id, "Metadata": {"verified": True}}
        resp, code, dur = make_request("PUT", "/product/meta-data", update_data)
        status = "PASS" if code == 200 else "FAIL"
        tests.append(("PUT /product/meta-data", status, f"{dur:.2f}ms"))
        
    # 2. Core Search
    print("\n[2/6] Testing Search...")
    queries = ["iphone", "sasta phone", "red mobile"]
    for q in queries:
        q_enc = urllib.parse.quote(q)
        resp, code, dur = make_request("GET", f"/search/product?query={q_enc}")
        status = "PASS" if code == 200 and len(resp.get('data', [])) > 0 else "FAIL"
        tests.append((f"GET /search '{q}'", status, f"{dur:.2f}ms"))

    # 3. Suggestions
    print("\n[3/6] Testing Suggestions...")
    resp, code, dur = make_request("GET", "/search/suggestions?query=sam")
    status = "PASS" if code == 200 and len(resp.get('suggestions', [])) > 0 else "FAIL"
    tests.append(("GET /suggestions", status, f"{dur:.2f}ms"))

    # 4. Trending
    print("\n[4/6] Testing Trending...")
    resp, code, dur = make_request("GET", "/product/trending")
    status = "PASS" if code == 200 and len(resp.get('data', [])) > 0 else "FAIL"
    tests.append(("GET /trending", status, f"{dur:.2f}ms"))

    # 5. Similar
    print("\n[5/6] Testing Similar...")
    # Use the product we created or a known one (e.g. 101)
    target = product_id if product_id else 101
    resp, code, dur = make_request("GET", f"/product/{target}/similar")
    status = "PASS" if code == 200 else "FAIL" # Might be empty but should 200
    tests.append(("GET /similar", status, f"{dur:.2f}ms"))
    
    # 6. Performance Summary
    print("\n=== RESULTS ===")
    print(f"{'ENDPOINT':<30} | {'STATUS':<6} | {'LATENCY':<10}")
    print("-" * 50)
    for name, status, lat in tests:
        print(f"{name:<30} | {status:<6} | {lat:<10}")
        
if __name__ == "__main__":
    run_suite()
