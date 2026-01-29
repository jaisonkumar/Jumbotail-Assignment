from faker import Faker
import random
from .models import Product
from .database import db

fake = Faker()
Faker.seed(42)

def generate_synthetic_data(count: int = 1000):
    print(f"Generating {count} synthetic products...")
    
    brands = ["Apple", "Samsung", "Xiaomi", "OnePlus", "Realme", "Vivo", "Oppo", "Nothing", "Google", "Motorola"]
    models = ["Pro", "Max", "Ultra", "Lite", "Plus", "FE", "SE", "Flip", "Fold"]
    colors = ["Red", "Blue", "Black", "White", "Silver", "Gold", "Green", "Purple"]
    
    for _ in range(count):
        brand = random.choice(brands)
        model = f"{brand} {fake.first_name() if random.random() < 0.2 else random.choice(models)} Phone"
        
        # Make some specific "iPhone" entries for testing
        if random.random() < 0.1:
            brand = "Apple"
            iphone_ver = random.randint(5, 17)
            suffix = random.choice(["", "Pro", "Max", "Pro Max", "Mini", "Plus"])
            model = f"iPhone {iphone_ver} {suffix}".strip()
        
        title = f"{model} {random.choice(['64GB', '128GB', '256GB', '512GB'])} {random.choice(colors)}"
        
        mrp = random.randint(5000, 150000)
        price = int(mrp * random.uniform(0.7, 0.95))
        
        description = f"Brand new {title}. {fake.sentence(nb_words=10)} Feature packed."
        
        sales_count = random.randint(0, 10000)
        recent_sales = int(sales_count * random.uniform(0.0, 0.3)) # Last 30 days
        
        p = Product(
            productId=db.next_id,
            title=title,
            description=description,
            mrp=mrp,
            price=price,
            stock=random.randint(0, 500),
            rating=round(random.uniform(3.0, 5.0), 1),
            sales_count=sales_count,
            recent_sales_count=recent_sales,
            return_rate=random.uniform(0.0, 0.2) if random.random() > 0.8 else random.uniform(0.0, 0.05), # Few products have high returns
            complaint_count=random.randint(0, 50) if random.random() > 0.9 else random.randint(0, 5),
            Metadata={
                "ram": f"{random.choice([4, 6, 8, 12, 16])}GB",
                "screen_size": f"{random.uniform(5.5, 6.9):.1f} inches",
                "brand": brand
            }
        )
        # Use direct add to avoid overhead/hooks if any
        db.add_product_direct(p)
    
    print("Data generation complete.")
