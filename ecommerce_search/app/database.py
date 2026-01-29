import sqlite3
import json
import os
from typing import List, Optional, Dict
from .models import Product, ProductCreate

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "products.db")

class ProductStore:
    def __init__(self):
        self.products: Dict[int, Product] = {}
        self.next_id = 101
        self._init_db()
        self._load_from_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _load_from_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, data FROM products')
        rows = cursor.fetchall()
        for row in rows:
            pid, data_json = row
            try:
                p_data = json.loads(data_json)
                product = Product(**p_data)
                self.products[pid] = product
                if pid >= self.next_id:
                    self.next_id = pid + 1
            except Exception as e:
                print(f"Error loading product {pid}: {e}")
        conn.close()
        print(f"Loaded {len(self.products)} products from DB.")

    def _save_to_db(self, product: Product):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO products (id, data) VALUES (?, ?)', 
                       (product.productId, product.json()))
        conn.commit()
        conn.close()

    def add_product(self, product_create: ProductCreate) -> Product:
        t_dict = product_create.dict()
        new_product = Product(productId=self.next_id, **t_dict)
        # Default sales_count to something random or 0? 
        # For now 0, but synthetic data generation will overwrite it.
        
        self.products[self.next_id] = new_product
        self._save_to_db(new_product)
        self.next_id += 1
        return new_product

    def add_product_direct(self, product: Product):
        """Used for bulk loading/bootstrapping"""
        self.products[product.productId] = product
        self._save_to_db(product)
        if product.productId >= self.next_id:
            self.next_id = product.productId + 1

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.products.get(product_id)

    def update_metadata(self, product_id: int, metadata: Dict[str, str]) -> Optional[Product]:
        if product_id in self.products:
            self.products[product_id].Metadata.update(metadata)
            self._save_to_db(self.products[product_id])
            return self.products[product_id]
        return None

    def get_all_products(self) -> List[Product]:
        return list(self.products.values())

# Global instance
db = ProductStore()
