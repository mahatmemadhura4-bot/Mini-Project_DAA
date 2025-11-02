# tsp_basic.py
# Basic Traveling Salesman Problem (TSP) controller.
#
# Exposes one main function:
#   find_basic_route(locations: List[str], coordinates: Dict[str, [lat, lon]])
# which returns (route_names_list, total_distance_km, estimated_time_min)

from typing import List, Dict, Tuple
import algos
import math

# Average speed assumption (urban, km/h)
DEFAULT_AVG_SPEED_KMH = 25.0


def find_basic_route(locations: List[str], coordinates: Dict[str, List[float]]) -> Tuple[List[str], float, float]:
    """
    Basic TSP solver using the nearest-neighbor heuristic.
    Returns a closed tour (start to start).
    """
    # Validate input
    if not locations or not coordinates:
        raise ValueError("locations and coordinates are required")

    # Ensure all locations have coordinates
    for name in locations:
        if name not in coordinates:
            raise ValueError(f"Missing coordinates for location: {name}")

    # Build ordered list of coordinates
    ordered_names = []
    ordered_coords = []
    for name in locations:
        ordered_names.append(name)
        latlon = coordinates[name]
        ordered_coords.append((float(latlon[0]), float(latlon[1])))

    n = len(ordered_names)
    if n == 0:
        return [], 0.0, 0.0
    if n == 1:
        return [ordered_names[0]], 0.0, 0.0

    # Build distance matrix
    matrix = algos.build_distance_matrix(ordered_coords)

    # Use nearest neighbor starting from the first location
    route_idx = algos.nearest_neighbor_route(matrix, start_idx=0)

    # Close the tour by returning to the starting point
    total_distance_km = algos.total_route_distance_from_indices(route_idx, matrix, closed=True)

    # Convert indices back to names and close the route
    route_names = [ordered_names[i] for i in route_idx] + [ordered_names[route_idx[0]]]

    # Estimate travel time
    estimated_time_min = (total_distance_km / DEFAULT_AVG_SPEED_KMH) * 60.0 if total_distance_km > 0 else 0.0

    return route_names, round(total_distance_km, 3), round(estimated_time_min, 2)
