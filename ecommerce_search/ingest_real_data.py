import json
import random
import os
import sys
from datetime import datetime, timedelta

# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from app.database import db
from app.models import Product

def ingest_data():
    print("Loading devices.json...")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))
    devices_path = os.path.join(script_dir, "devices.json")
    
    try:
        with open(devices_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"devices.json not found at {devices_path}. Run curl command first.")
        return

    print(f"Found {len(data)} brands/series.")
    
    models = []
    
    # Check for RECORDS key (based on file view)
    records = data.get("RECORDS", [])
    if not records and isinstance(data, list):
        records = data
        
    for entry in records:
        full_name = entry.get("name", "")
        if not full_name:
            continue
            
        # Infer brand from first word
        parts = full_name.split(" ", 1)
        if len(parts) > 0:
            brand = parts[0]
            model = parts[1] if len(parts) > 1 else full_name
            models.append((brand, model))
    
    print(f"Loaded {len(models)} unique base models.")
    
    # Variations
    colors = ["Black", "White", "Silver", "Gold", "Blue", "Red", "Green", "Purple", "Grey"]
    storages = ["64GB", "128GB", "256GB", "512GB", "1TB"]
    
    # Desired total
    TARGET = 12000
    
    generated = 0
    batch = []
    
    random.shuffle(models)
    
    # Infinite loop over models until target is reached
    while generated < TARGET:
        for brand, model in models:
            if generated >= TARGET: 
                break
                
            # Randomly pick specs for validity
            color = random.choice(colors)
            storage = random.choice(storages)
            
            title = f"{brand} {model} {storage} {color}"
            
            # Simple Price Logic
            base_price = 10000
            if brand.lower() in ["apple", "google", "samsung", "sony"]:
                base_price = 40000
            elif brand.lower() in ["oneplus", "nothing"]:
                base_price = 30000
            
            # Add volatility
            price = int(base_price * random.uniform(0.5, 3.0))
            
            # Smart Rating
            rating = round(random.uniform(3.5, 5.0), 1)
            
            p = Product(
                productId=db.next_id,
                title=title,
                description=f"Original {brand} {model} with {storage} storage in {color}. Best in class features.",
                mrp=int(price * 1.2),
                price=price,
                stock=random.randint(0, 100),
                rating=rating,
                sales_count=random.randint(0, 5000),
                recent_sales_count=random.randint(0, 500),
                return_rate=random.uniform(0.0, 0.1),
                complaint_count=random.randint(0, 10),
                launch_date=launch_date,
                Metadata={
                    "brand": brand,
                    "color": color, 
                    "storage": storage,
                    "category": "phone"
                }
            )
            
            db.add_product_direct(p) # Using direct insertion for speed (bypassing ID incrementer logic overhead if any)
            generated += 1
            if generated % 1000 == 0:
                print(f"Generated {generated} products...")
                
    print(f"Successfully ingested {generated} real-world based products.")

if __name__ == "__main__":
    ingest_data()
