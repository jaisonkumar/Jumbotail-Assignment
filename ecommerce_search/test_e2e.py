import urllib.request
import json
import sys
import time

BASE_URL = "http://localhost:8001/api/v1"

def make_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req.data = json_data
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8')), response.getcode()
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode('utf-8')), e.code
    except Exception as e:
        print(f"Request failed: {e}")
        return None, 500

def test_endpoints():
    print("--- Starting End-to-End API Verification ---")
    
    # 1. Test POST /product
    print("\n1. Testing Product Creation...")
    new_product = {
        "title": "SuperPhone X 2026",
        "description": "The latest and greatest phone with AI.",
        "mrp": 99999,
        "price": 89999,
        "stock": 50,
        "rating": 4.8,
        "currency": "Rupee"
    }
    resp, code = make_request("POST", "/product", new_product)
    if code == 201:
        pid = resp['productId']
        print(f"SUCCESS: Created product with ID {pid}")
    else:
        print(f"FAILED: {code} - {resp}")
        return

    # 2. Test PUT /product/meta-data
    print("\n2. Testing Metadata Update...")
    meta_update = {
        "productId": pid,
        "Metadata": {
            "ram": "16GB",
            "processor": "Snapdragon 9 Gen 5"
        }
    }
    resp, code = make_request("PUT", "/product/meta-data", meta_update)
    if code == 200 and resp['Metadata']['ram'] == "16GB":
         print(f"SUCCESS: Updated metadata for ID {pid}")
    else:
         print(f"FAILED: {code} - {resp}")

    # 3. Test Search (Basic)
    print("\n3. Testing Search 'superphone'...")
    resp, code = make_request("GET", "/search/product?query=superphone")
    found = False
    if code == 200:
        for p in resp['data']:
            if p['productId'] == pid:
                found = True
                break
        if found:
            print("SUCCESS: Found newly created product in search.")
        else:
            print("FAILED: Product not found in search results.")
    else:
        print(f"FAILED: Search error {code}")

    # 4. Test Intent Search 'sasta'
    print("\n4. Testing Intent 'sasta iphone' (Expect cheap ones top)...")
    resp, code = make_request("GET", "/search/product?query=sasta%20iphone")
    if code == 200 and len(resp['data']) > 1:
        first_price = resp['data'][0]['price']
        last_price = resp['data'][-1]['price']
        print(f"Top result price: {first_price}, Last result price: {last_price}")
        if first_price <= last_price:
             print("SUCCESS: Cheaper products are ranked higher (or equal).")
        else:
             print("WARNING: Ranking might need tuning for 'sasta'.")
    elif code == 200:
        print("NOTE: Not enough results to verify sorting.")
    else:
        print(f"FAILED: {code}")

    # 5. Test Fuzzy Search 'ifone'
    print("\n5. Testing Fuzzy 'ifone'...")
    resp, code = make_request("GET", "/search/product?query=ifone")
    if code == 200 and len(resp['data']) > 0:
        match = any("iphone" in p['title'].lower() for p in resp['data'])
        if match:
             print("SUCCESS: 'ifone' query returned iPhones.")
        else:
             print("FAILED: 'ifone' did not return expected matches.")
    else:
        print(f"FAILED: {code}")

    print("\n--- Verification Finished ---")

if __name__ == "__main__":
    # Wait a sec for server to be fully ready if just started
    time.sleep(1)
    test_endpoints()
