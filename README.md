# E-commerce Search Engine

A high-performance, intent-aware search engine built with **FastAPI** and **RapidFuzz**. It delivers sub-200ms latency on a catalog of 14,000+ real-world products, featuring intelligent ranking, fuzzy matching, and personalized query understanding.

## 🚀 Key Features

### 🧠 Advanced Search Intelligence
- **Intent-Adaptive Ranking**: Dynamically switches scoring profiles based on user intent (e.g., "Budget", "Premium", "Spec-Focused").
- **Smart Token Coverage**: Normalizes specifications (e.g., "256 gb" → "256gb") and searches across metadata for high partial-match accuracy.
- **Adaptive Budgeting**: Automatically detects price intent relative to the *median price* of results (e.g., "Sasta" works differently for phones vs. covers).
- **Diversity Guardrails**: Penalizes clustering of identical models to ensure a diverse top-k result.
- **Explainability**: Returns reasons for ranking (e.g., "High Match", "Trending", "Within Budget") with confidence scores.

### ⚡ Performance & Data
- **Real-World Catalog**: Ingests **10,633 real mobile phone models** to generate >14,000 realistic SKUs.
- **Optimized Latency**: **~170ms** average response time using `rapidfuzz` and multi-pass ranking optimizations.
- **Persistence**: SQLite-backed in-memory storage for high read throughput and durability.

---

## 🛠️ Installation & Setup

1. **Clone & Environment Setup**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r ecommerce_search/requirements.txt
   ```

3. **Ingest Real Data (One-time Setup)**
   Download the device list and generate the catalog:
   ```bash
   # Download source JSON
   curl -o ecommerce_search/devices.json https://raw.githubusercontent.com/ilyasozkurt/mobilephone-brands-and-models/master/devices.json
   
   # Run ingestion script
   python ecommerce_search/ingest_real_data.py
   ```

4. **Start the Server**
   ```bash
   uvicorn ecommerce_search.app.main:app --reload --port 8001
   ```

---

## 📡 API Endpoints

Explore the interactive Swagger UI at: `http://localhost:8001/docs`

### 🔍 Search & Discovery
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/search/product` | **Main Search**. Supports queries like "sasta iphone", "red samsung under 20k". |
| `GET` | `/api/v1/search/suggestions` | **Autocomplete**. Returns title suggestions based on prefix & fuzzy match. |
| `GET` | `/api/v1/product/trending` | **Trending**. Returns products with high recent sales momentum. |
| `GET` | `/api/v1/product/{id}/similar` | **Recommendations**. Content-based similarity (Brand + Specs + Price). |

### 📦 Product Management
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/product` | Add a new product to the catalog. |
| `PUT` | `/api/v1/product/meta-data` | Update arbitrary metadata (e.g., RAM, Color). |

---

## 🧪 Verification & Testing

The project includes several scripts to validate functionality and performance:

- **End-to-End Test**: Verifies all API endpoints.
  ```bash
  python ecommerce_search/final_verify.py
  ```

- **Performance Benchmark**: Measures latency across various query types.
  ```bash
  python ecommerce_search/check_performance.py
  ```

---

## 📂 Project Structure

```
ecommerce_search/
├── app/
│   ├── main.py           # API Routes & Entry Point
│   ├── service.py        # Core Ranking Engine (The Brain)
│   ├── models.py         # Pydantic Schemas
│   ├── database.py       # Persistence Layer
│   └── utils.py          # Data Utilities
├── devices.json          # Raw source data (Real Models)
├── ingest_real_data.py   # Catalog Generation Script
├── check_performance.py  # Latency Benchmark
└── final_verify.py       # E2E Testing Script
```
