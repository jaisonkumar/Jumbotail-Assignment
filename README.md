# E-commerce Search Engine Microservice

## Overview
A high-performance search engine microservice for an electronics e-commerce platform. Built with **FastAPI**, it features fuzzy matching, intent understanding (e.g., "sasta"), and a weighted ranking algorithm based on sales, ratings, and price.

## Features
- **BOOTSTRAPPED Catalog**: Automatically generates 1000+ synthetic products using `Faker`.
- **Fuzzy Search**: Handles typos (e.g., "ifone") using `thefuzz`.
- **Smart Ranking**: Ranks based on:
  - Text Relevance
  - Sales Popularity (Logarithmic boost)
  - Ratings
  - Stock Availability
- **Intent Recognition**:
  - "Sasta" / "Cheap" -> Prioritizes lower prices.
  - "Premium" -> Prioritizes higher prices.
  - "Under Xk" -> Filters/Penalizes prices above limit.

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access Swagger UI**:
   Open [http://localhost:8000/docs](http://localhost:8000/docs) to test APIs interacting.

## API Endpoints

### 1. Store Product
`POST /api/v1/product`
Create a new product manually.

### 2. Update Metadata
`PUT /api/v1/product/meta-data`
Update arbitrary metadata (RAM, Screen Size, etc.).

### 3. Search
`GET /api/v1/search/product?query=...`
Search for products.
Examples:
- `?query=iphone 15`
- `?query=sasta samsung phone`
- `?query=red laptop under 50k`

## Project Structure
- `app/main.py`: Entry point and API routes.
- `app/service.py`: Search and Ranking logic.
- `app/models.py`: Pydantic data models.
- `app/database.py`: In-memory store with SQLite persistence (`data/products.db`).
- `app/utils.py`: Synthetic data generator.
