import urllib.request
import json
import time

BASE_URL = "http://localhost:8001/api/v1"

def make_request(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def verify_features():
    print("--- Verifying New Endpoints ---")
    
    # 1. Suggestions
    print("Testing /search/suggestions?query=ip...")
    resp = make_request("/search/suggestions?query=ip")
    if resp and "suggestions" in resp:
        print(f"Suggestions: {resp['suggestions']}")
    else:
        print("Suggestions Failed")

    # 2. Trending
    print("\nTesting /product/trending...")
    resp = make_request("/product/trending")
    if resp and "data" in resp:
        print(f"Top 3 Trending: {[p['title'] for p in resp['data'][:3]]}")
    else:
        print("Trending Failed")

    # 3. Similar
    print("\nTesting /product/{id}/similar...")
    # Get a product ID first
    search_resp = make_request("/search/product?query=phone")
    if search_resp and search_resp['data']:
        pid = search_resp['data'][0]['productId']
        title = search_resp['data'][0]['title']
        print(f"Finding similar to [{pid}] {title}...")
        
        sim_resp = make_request(f"/product/{pid}/similar")
        if sim_resp and "data" in sim_resp:
             print(f"Similar found: {[p['title'] for p in sim_resp['data'][:3]]}")
    else:
        print("Could not find product to test similarity.")

if __name__ == "__main__":
    verify_features()
