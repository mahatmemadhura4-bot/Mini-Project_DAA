# route_model.py
"""
route_model.py
--------------
Utility module that:
 - geocodes place names (OpenCage)
 - builds coordinates dict
 - selects & runs TSP algorithm (brute-force for small n or hybrid MST+TSP for larger n)
 - returns a consistent result dict suitable for JSON response

Functions:
 - geocode_place(place, api_key=None) -> (lat, lon) or raises
 - generate_optimized_path(place_names, api_key=None, coordinates=None, brute_force_threshold=8)
"""

import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional

load_dotenv()

# prefer OPENCAGE_API_KEY env var name to match your app.py
DEFAULT_OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

# import algorithms (ensure algos.py provides tsp_bruteforce and find_optimized_route)
from algos import tsp_bruteforce, find_optimized_route


# -------------------------
# Helper: Geocode a single place (OpenCage)
# -------------------------
def geocode_place(place: str, api_key: Optional[str] = None) -> Tuple[float, float]:
    """
    Geocode `place` using OpenCage Geocoding API.
    Returns (lat, lon).
    Raises ValueError on failure.
    """
    key = api_key or DEFAULT_OPENCAGE_API_KEY
    if not key:
        raise ValueError("OpenCage API key required (OPENCAGE_API_KEY env var or api_key arg).")

    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {"q": place, "key": key, "limit": 1}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        doc = resp.json()
    except requests.RequestException as e:
        raise ValueError(f"Geocoding request failed: {e}")

    results = doc.get("results") or []
    if not results:
        raise ValueError(f"Location not found: {place}")

    geometry = results[0].get("geometry")
    if not geometry or "lat" not in geometry or "lng" not in geometry:
        raise ValueError(f"Invalid geocoding response for: {place}")

    return float(geometry["lat"]), float(geometry["lng"])


# -------------------------
# Main: Generate optimized path from place names or coordinates
# -------------------------
def generate_optimized_path(
    place_names: List[str],
    api_key: Optional[str] = None,
    coordinates: Optional[Dict[str, Tuple[float, float]]] = None,
    brute_force_threshold: int = 8,
) -> Dict:
    """
    Given a list of place names (strings), either:
      - use provided `coordinates` mapping (name -> (lat, lon)), or
      - geocode each place with OpenCage to create coordinates.

    Then select algorithm:
      - if n <= brute_force_threshold -> tsp_bruteforce (exact)
      - else -> find_optimized_route (hybrid MST + TSP)

    Returns a dict:
    {
      "optimized_path": [...],
      "total_distance": float (km),
      "estimated_time": float (minutes),
      "route_coordinates": [[lat, lon], ...],
      "message": str (human-friendly)
    }
    Raises ValueError for invalid inputs.
    """
    if not place_names or len(place_names) < 2:
        raise ValueError("At least two place names are required.")

    # build coordinates dict if not provided
    coords = {} if coordinates is None else dict(coordinates)  # shallow copy

    # geocode missing entries
    for place in place_names:
        if place in coords:
            continue
        try:
            lat, lon = geocode_place(place, api_key=api_key)
            coords[place] = (lat, lon)
        except Exception as e:
            # bubble up with clear message
            raise ValueError(f"Geocoding failed for '{place}': {e}")

    # validate coords for all requested places
    missing = [p for p in place_names if p not in coords]
    if missing:
        raise ValueError(f"No coordinates for places: {missing}")

    # choose algorithm
    n = len(place_names)
    if n <= brute_force_threshold:
        # tsp_bruteforce returns (optimized_path:list, total_distance:float, total_time_min:float)
        result = tsp_bruteforce(place_names, coords)
        # tsp_bruteforce in some variants returns either (path, dist) or (path, dist, time).
        # Normalize:
        if isinstance(result, tuple) and len(result) == 3:
            optimized_path, total_distance_km, estimated_time_min = result
        elif isinstance(result, tuple) and len(result) == 2:
            optimized_path, total_distance_km = result
            avg_speed_kmh = 40
            estimated_time_min = (total_distance_km / avg_speed_kmh) * 60
        else:
            raise ValueError("tsp_bruteforce returned unexpected format.")
        algo_used = "brute_force_tsp"
    else:
        # find_optimized_route returns dict or tuple depending on your algos.py — normalize here
        result = find_optimized_route(place_names, coords)
        if isinstance(result, dict):
            optimized_path = result.get("optimized_path") or result.get("route") or []
            total_distance_km = result.get("total_distance") or result.get("total_distance_km") or 0
            # find_optimized_route earlier returned estimated_time in hours sometimes; normalize to minutes
            est = result.get("estimated_time") or result.get("estimated_time_hr") or result.get("estimated_time_min") or 0
            # If estimated_time looks like hours (< 10 generally) treat as hours
            if est and est < 10 and total_distance_km > 0:
                # ambiguous: treat as hours if small; but make robust: check keys
                if "estimated_time_hr" in result or "estimated_time" in result and result.get("estimated_time") <= 10:
                    estimated_time_min = float(est) * 60
                else:
                    estimated_time_min = float(est)
            else:
                estimated_time_min = float(est)
            algo_used = "mst_preorder_tsp"
        elif isinstance(result, tuple) and len(result) == 3:
            optimized_path, total_distance_km, estimated_time_min = result
            algo_used = "mst_preorder_tsp"
        else:
            raise ValueError("find_optimized_route returned unexpected format.")

    # prepare route coordinates (lat, lon) in order
    route_coords = []
    for name in optimized_path:
        if name in coords:
            route_coords.append([coords[name][0], coords[name][1]])
        else:
            # skip or raise — here we skip silently
            continue

    message = f"Route computed using {algo_used}."

    return {
        "optimized_path": optimized_path,
        "total_distance": round(float(total_distance_km), 2),
        "estimated_time": round(float(estimated_time_min), 2),  # minutes
        "route_coordinates": route_coords,
        "message": message
    }


# -------------------------
# Optional: small test-run
# -------------------------
if __name__ == "__main__":
    # quick local test (requires OPENCAGE_API_KEY in .env)
    places = ["Pune, India", "Mumbai, India", "Nashik, India"]
    try:
        out = generate_optimized_path(places)
        import json
        print(json.dumps(out, indent=2))
    except Exception as e:
        print("Test failed:", e)
