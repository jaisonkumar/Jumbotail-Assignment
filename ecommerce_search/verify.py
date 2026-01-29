import sys
import os

# Add local directory to path
sys.path.append(os.getcwd())

try:
    from app.database import db
    from app.service import search_service
    from app.utils import generate_synthetic_data
except ImportError:
    print("Dependencies missing. Please install requirements.txt first.")
    sys.exit(1)

def run_tests():
    print("--- Starting Verification ---")
    
    # 1. Generate Data
    print("Generating data...")
    generate_synthetic_data(100) # Smaller set for quick test
    print(f"Total products: {len(db.get_all_products())}")
    
    # 2. Test Cases
    queries = [
        ("iphone", "Basic Search"),
        ("sasta iphone", "Intent: Low Price"),
        ("ifone", "Fuzzy Search (Typo)"),
        ("red phone", "Attribute Search"),
        ("under 50k phone", "Price Constraint"),
    ]
    
    for query, desc in queries:
        print(f"\nTest: '{query}' ({desc})")
        results = search_service.search(query, limit=5)
        for p in results:
            print(f"  - [{p.productId}] {p.title} | Price: {p.price} | Rating: {p.rating} | Sales: {p.sales_count}")
            
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    run_tests()
