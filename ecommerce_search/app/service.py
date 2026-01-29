import random
import re
import math
from typing import List, Dict, Any, Tuple
from .database import db
from .models import Product
from rapidfuzz import fuzz

class IntentProfile:
    def __init__(self, name: str, price_weight: float, rating_weight: float, 
                 sales_weight: float, recent_sales_weight: float, stock_weight: float):
        self.name = name
        self.price_weight = price_weight
        self.rating_weight = rating_weight
        self.sales_weight = sales_weight
        self.recent_sales_weight = recent_sales_weight
        self.stock_weight = stock_weight

class SearchService:
    def get_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Autocomplete suggestions based on product titles"""
        query = query.lower().strip()
        if not query:
            return []
        
        all_products = db.get_all_products()
        suggestions = set()
        
        # Simple prefix match first
        for p in all_products:
            title_lower = p.title.lower()
            if title_lower.startswith(query):
                suggestions.add(p.title)
            # Check description words for broader suggestions? Maybe too noisy.
            # Let's stick to titles for now.
            if len(suggestions) >= limit * 2: 
                break
                
        # If few matches, try fuzzy matching token
        if len(suggestions) < limit:
             for p in all_products:
                 if fuzz.partial_ratio(query, p.title.lower()) > 80:
                     suggestions.add(p.title)
                     if len(suggestions) >= limit * 2: break
        
        return list(suggestions)[:limit]

    def get_trending(self, limit: int = 10) -> List[Product]:
        """Get products with highest recent sales momentum"""
        all_products = db.get_all_products()
        # Sort by recent_sales_count desc
        trending = sorted(all_products, key=lambda p: p.recent_sales_count, reverse=True)
        return trending[:limit]

    def get_similar_products(self, product_id: int, limit: int = 5) -> List[Product]:
        """Content-based similarity (Same brand, similar specs/title)"""
        target = db.get_product(product_id)
        if not target:
            return []
            
        all_products = db.get_all_products()
        candidates = []
        
        for p in all_products:
            if p.productId == product_id:
                continue
                
            score = 0
            # Same brand boost
            if target.Metadata.get("brand") == p.Metadata.get("brand"):
                score += 30
                
            # Title similarity
            score += fuzz.token_set_ratio(target.title, p.title)
            
            # Price proximity (within 20%)
            price_diff_ratio = abs(target.price - p.price) / (target.price + 1)
            if price_diff_ratio < 0.2:
                score += 20
                
            candidates.append((p, score))
            
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in candidates[:limit]]

    def __init__(self):
        # 3. Token Importance Dictionary
        self.TOKEN_WEIGHTS = {
            # Core Terms (High Importance)
            "iphone": 2.0, "samsung": 2.0, "pixel": 2.0, "oneplus": 2.0, "xiaomi": 2.0,
            "realme": 2.0, "vivo": 2.0, "oppo": 2.0, "nothing": 2.0, "motorola": 2.0,
            "apple": 2.0, "macbook": 2.0, "dell": 2.0, "hp": 2.0, "sony": 2.0,
            
            # Modifiers (Medium)
            "pro": 1.5, "max": 1.5, "plus": 1.5, "ultra": 1.5, "mini": 1.2,
            "5g": 1.2, "cover": 1.5, "case": 1.5, "charger": 1.5, "screen": 1.5,
            "guard": 1.5, "glass": 1.5, "earpods": 1.5, "watch": 1.5,
            "red": 1.3, "blue": 1.3, "black": 1.3, "white": 1.3, "gold": 1.3, "silver": 1.3,
            "64gb": 1.4, "128gb": 1.4, "256gb": 1.4, "512gb": 1.4, "1tb": 1.4,
            
            # Intents (Handled separately but weighted if matched)
            "sasta": 1.0, "cheap": 1.0, "budget": 1.0, "premium": 1.0, "latest": 1.0,
            
            # Noise (Low)
            "phone": 0.5, "mobile": 0.5, "smartphone": 0.5, "device": 0.5, "gadget": 0.5,
            "chahiye": 0.1, "wala": 0.1, "hai": 0.1, "me": 0.1, "under": 0.5, "rupees": 0.1,
            "best": 0.5, "top": 0.5
        }
        
        # 5. Intent Profiles
        self.PROFILES = {
            "default": IntentProfile("Default", 1.0, 1.0, 1.0, 1.0, 1.0),
            "budget": IntentProfile("Budget", 2.5, 0.8, 1.2, 0.5, 1.0), # High price sensitivity
            "premium": IntentProfile("Premium", -1.5, 1.5, 1.0, 1.5, 0.8), # Negative price weight (higher is fine/better), high rating
            "spec": IntentProfile("Spec", 0.5, 1.2, 0.8, 1.5, 1.0), # Focus on recent/rating
        }

    def _analyze_intent(self, query: str) -> Tuple[str, dict]:
        """
        Analyze query to determine user intent and extract constraints.
        Returns: (profile_name, constraints_dict)
        """
        q = query.lower()
        constraints = {"price_limit": None, "intent_strength": "weak"}
        profile = "default"
        
        # 4. Intent Strength & 5. Categories
        if any(w in q for w in ["sasta", "cheap", "budget", "low price", "kam daam", "economy", "value"]):
            profile = "budget"
            constraints["intent_strength"] = "strong"
        elif any(w in q for w in ["premium", "expensive", "flagship", "pro", "high end", "luxury"]):
            profile = "premium"
            constraints["intent_strength"] = "medium"
        elif any(w in q for w in ["latest", "new", "recent", "2025", "2026", "fresh"]):
            profile = "spec"
            constraints["is_latest"] = True
            
        # Price Constraints extraction
        price_match = re.search(r'under\s*(\d+)k?', q) or re.search(r'(\d+)k', q)
        if price_match:
            try:
                val = price_match.group(1)
                constraints["price_limit"] = int(val) * 1000 if 'k' in q or len(val) < 3 else int(val)
                profile = "budget" # Explicit limit implies budget consciousness
            except:
                pass
                
        # Category Intent
        if any(w in q for w in ["cover", "case", "guard", "glass"]):
            constraints["category"] = "accessory"
        elif any(w in q for w in ["phone", "mobile", "iphone", "samsung"]):
            constraints["category"] = "phone"
            
        return profile, constraints

    def _normalize_token(self, token: str) -> str:
        """Unify spec tokens e.g. '256 gb' -> '256gb'"""
        # Collapse space between number and unit
        return re.sub(r'(\d+)\s+(gb|mb|tb|mm|mah)', r'\1\2', token)

    def _calculate_token_relevance(self, query: str, product: Product) -> Tuple[float, float]:
        """
        2. separate Match Quality from Coverage.
        Returns: (quality_score, coverage_score)
        """
        # 1. Token Coverage Refinement: Normalize and Include Metadata
        normalized_query = self._normalize_token(query.lower())
        query_tokens = normalized_query.split()
        if not query_tokens:
            return 0.0, 0.0
            
        total_weight = 0.0
        matched_weight = 0.0
        
        # Construct full search text including metadata
        meta_values = " ".join([str(v) for v in product.Metadata.values()])
        text = self._normalize_token((product.title + " " + product.description + " " + meta_values).lower())
        
        for token in query_tokens:
            weight = self.TOKEN_WEIGHTS.get(token, 1.0)
            total_weight += weight
            
            # Use wider check (substring match in full text)
            if token in text:
                matched_weight += weight
            else:
                pass
                
        coverage_score = (matched_weight / total_weight) * 100 if total_weight > 0 else 0
        
        # Base fuzzy score for "Quality"
        # We assume if coverage is high, quality is high, but text fuzziness refines it
        # Fuzz title match against query
        quality_score = fuzz.token_set_ratio(normalized_query, product.title.lower())
        
        return quality_score, coverage_score
    
    def _is_category_mismatch(self, query_constraints: dict, product: Product) -> bool:
        """6. Category Consistency Penalty"""
        intended_cat = query_constraints.get("category")
        if not intended_cat:
            return False
            
        # 2. Category Detection: Use explicit field first
        prod_cat = product.Metadata.get("category", "")
        if prod_cat:
            if intended_cat == "phone" and prod_cat != "phone": return True
            if intended_cat == "accessory" and prod_cat != "accessory": return True
            return False

        # Fallback to title keywords if explicit category missing
        is_accessory_prod = any(x in product.title.lower() for x in ["cover", "case", "glass", "guard", "protector"])
        
        if intended_cat == "phone" and is_accessory_prod:
            return True
        if intended_cat == "accessory" and not is_accessory_prod:
            return True
            
        return False

    def search(self, query: str, limit: int = 20) -> List[dict]:
        all_products = db.get_all_products()
        query = query.strip()
        if not query:
            return [{"product": p, "relevance_code": ["Browsing"]} for p in all_products[:limit]]
            
        profile_name, constraints = self._analyze_intent(query)
        profile = self.PROFILES[profile_name]
        
        # 11. Multi-Pass Ranking
        # Pass 1: Light Filtering (Coverage & Price Cap Hard-ish check)
        candidates = []
        
        clean_query = query.lower()
        if constraints.get("price_limit"):
            # Clean query of price terms for better matching
            clean_query = re.sub(r'under\s*\d+k?', '', clean_query).strip()

        for p in all_products:
            # 1. Soft Relevance Tiers via Score
            quality, coverage = self._calculate_token_relevance(clean_query, p)
            
            # Pass 1 Filter: Must have some coverage OR good fuzzy quality
            if coverage < 30 and quality < 30:
                continue
                
            # 6. Category Mismatch (Severe Penalty but not removal)
            cat_penalty = 0
            if self._is_category_mismatch(constraints, p):
                cat_penalty = 50 
            
            candidates.append({
                "product": p,
                "quality": quality,
                "coverage": coverage,
                "cat_penalty": cat_penalty
            })
            
        # Optimization: Pre-Ranking for broad queries
        # If we have too many candidates, running full scoring is slow.
        # Filter top 1000 by simple heuristic (Sales or Rating) first.
        if len(candidates) > 1000:
            candidates.sort(key=lambda x: x["product"].sales_count, reverse=True)
            candidates = candidates[:1000]
            
        # Pass 2: Heavy Scoring on Candidates
        scored_results = []
        
        # 3. Adaptive Budgeting: Calculate median price of candidates for relative contexts
        median_price = 30000 
        if candidates:
            prices = sorted([c["product"].price for c in candidates])
            median_price = prices[len(prices)//2]

        seen_models = set()
        
        for item in candidates:
            p = item["product"]
            reasons = []
            score = 0
            
            # --- Text Relevance ---
            # Blend quality (fuzzy) and coverage (tokens present)
            # 3. Token Importance built into coverage already via weights
            text_score = (item["quality"] * 0.4) + (item["coverage"] * 0.6)
            score += text_score
            
            if text_score > 80:
                reasons.append("High Match")
            
            # --- Business Metrics ---
            
            # 9. Popularity Momentum
            # Blend total sales + recent sales * multiplier
            popularity_score = math.log(p.sales_count + 1) + (math.log(p.recent_sales_count + 1) * 2)
            score += (popularity_score * 2.0 * profile.sales_weight)
            
            if p.recent_sales_count > 100:
                reasons.append("Trending")
            
            # Rating Boost
            score += (p.rating * 5.0 * profile.rating_weight)
            if p.rating > 4.5:
                reasons.append("Top Rated")

            # 7. Stock Saturation
            # Out (-50), Low (<10, -10), Healthy (>10, +10)
            if p.stock == 0:
                score -= 50
                reasons.append("Out of Stock")
            elif p.stock < 10:
                score -= 10
            else:
                score += 10
                
            # 8. Negative Signals
            # Return Rate > 10% -> Heavy penalty
            if p.return_rate > 0.10:
                score -= 30
                reasons.append("High Returns")
            
            # --- Price Logic (Adaptive) ---
            # 10. Non-linear Price Sensitivity
            price_limit = constraints.get("price_limit")
            if price_limit:
                if p.price <= price_limit:
                    score += 20 # Met constraint
                    reasons.append("Within Budget")
                else:
                    # Soft penalty: decay as price moves away
                    diff_ratio = (p.price - price_limit) / (price_limit + 1)
                    penalty = 20 + (diff_ratio * 50)
                    score -= penalty
            
            if profile_name == "Budget":
                # Sweet spot is median or lower
                # If price is lower than median, boost.
                if p.price < median_price:
                    score += 15
                elif p.price > median_price * 1.5:
                    score -= 10
            elif profile_name == "Premium":
                # Higher price is good signal for premium
                if p.price > median_price:
                    score += 15
                
            # Apply Category Penalty
            score -= item["cat_penalty"]
            if item["cat_penalty"] > 0:
                reasons.append("Category Mismatch")

            # 5. Diversity Guardrail
            # Penalize if we've seen this model base already to prevent clutter
            # Assuming title "Brand ModelVariant ..." -> extract "Brand Model" roughly
            model_key = " ".join(p.title.split()[:2]) 
            if model_key in seen_models:
                score -= 15 # Diversity penalty
            seen_models.add(model_key)
                
            # 13. Confidence Score (Composite)
            # Relevance + Intent Satisfaction + Metadata Health
            confidence = (text_score * 0.6) + (20 if not reasons else 0) # Placeholder logic enhancement
            if "Within Budget" in reasons: confidence += 10
            if "Category Mismatch" not in reasons: confidence += 10
            confidence = min(100, max(0, confidence))
            
            scored_results.append({
                "product": p,
                "score": score,
                "confidence": confidence,
                "reasons": reasons[:3], # 12. Top 3 reasons
                "debug_score": score
            })
            
        # Sort
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Format for output (Product object usually doesn't take extra fields easily if strictly typed, 
        # so we might need to rely on Metadata or just return the object.
        # The prompt asked to "generate explainable output". 
        # I will inject reasons into Metadata for display purposes.)
        
        final_list = []
        for item in scored_results[:limit]:
            p = item["product"]
            # 6. Fix Mutation: Clone properly to avoid side effects
            # Create a lightweight dict copy for response or shallow copy object
            # For simplicity in this Pydantic/Dict hybrid setup:
            p_response = p.copy() 
            p_response.Metadata = p.Metadata.copy() # Shallow copy of dict
            
            p_response.Metadata["ranking_reasons"] = item["reasons"]
            p_response.Metadata["confidence"] = f"{item['confidence']:.1f}%"
            final_list.append(p_response)
            
        return final_list

search_service = SearchService()
