# tsp_modified.py
# High-level modified TSP controller that uses algos.py
#
# Exposes one main function:
#   find_optimized_route(locations: List[str], coordinates: Dict[str, [lat,lon]])
# which returns (optimized_route_names_list, total_distance_km, estimated_time_min)

from typing import List, Dict, Tuple
import algos
import math

# Average speed assumption (urban, km/h). Adjust as needed.
DEFAULT_AVG_SPEED_KMH = 25.0


def _prepare(coords_dict: Dict[str, List[float]]) -> Tuple[List[str], List[Tuple[float,float]]]:
    """
    Normalize inputs: returns (ordered_names, ordered_coords)
    The input coords_dict keys are names and values are [lat, lon].
    Ordering is deterministic by insertion order of keys given by caller.
    """
    names = []
    coords = []
    for name, latlon in coords_dict.items():
        names.append(name)
        coords.append((float(latlon[0]), float(latlon[1])))
    return names, coords


def _indices_for_names(names: List[str], requested_order: List[str]) -> List[int]:
    """
    Map the requested_order list of names to indices in names list.
    """
    index_map = {name: i for i, name in enumerate(names)}
    return [index_map[name] for name in requested_order]


def find_optimized_route(locations: List[str], coordinates: Dict[str, List[float]]) -> Tuple[List[str], float, float]:
    """
    Main entry for app.py to call.
    - locations: list of names the user provided (used to preserve ordering / labels)
    - coordinates: dict mapping name -> [lat, lon] for each name in locations (may include custom names)
    Returns:
      optimized_route_names (list of strings in visiting order),
      total_distance_km (float),
      estimated_time_min (float)
    Notes:
      - The algorithm builds a distance matrix (Haversine), uses Prim's MST to get a skeleton,
        then nearest-neighbor + 2-opt to produce a practical TSP route.
      - The returned route will be a closed tour (returns to start).
    """
    # Validate inputs
    if not locations or not coordinates:
        raise ValueError("locations and coordinates are required")

    # Ensure coordinates include all requested location names
    for name in locations:
        if name not in coordinates:
            raise ValueError(f"Missing coordinates for location: {name}")

    # Create a consistent names list and coords array matching the 'locations' order.
    # Use user-provided locations order to build coords list (so result uses the same labels).
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

    # Optional: get MST edges (not strictly required for NN heuristic but can guide improvement)
    mst_edges = algos.prims_mst(matrix)

    # Convert edges to adjacency if needed (not mandatory here)
    # But we will use nearest-neighbor starting from each node and pick best start
    best_route_idx = None
    best_distance = float('inf')

    # Try nearest neighbor starting from every node (small n -> affordable)
    for start in range(n):
        route_idx = algos.nearest_neighbor_route(matrix, start_idx=start)
        # Make it a closed tour by appending start at end
        # (we'll run 2-opt on the open route; two_opt expects non-closed route)
        # Apply 2-opt improvement
        improved = algos.two_opt(route_idx, matrix)
        # Now compute closed distance
        total_d = algos.total_route_distance_from_indices(improved, matrix, closed=True)
        if total_d < best_distance:
            best_distance = total_d
            best_route_idx = improved

    # best_route_idx is a list of node indices in visiting order (not closed)
    # Convert indices to names and append start at end to make closed tour
    optimized_indices = best_route_idx[:]
    # For presentation it's often nice to return closed tour: append first index
    optimized_indices_closed = optimized_indices + [optimized_indices[0]]

    optimized_names = [ordered_names[i] for i in optimized_indices_closed]
    total_distance_km = best_distance

    # Estimate time in minutes using average speed
    if total_distance_km <= 0:
        estimated_time_min = 0.0
    else:
        estimated_time_min = (total_distance_km / DEFAULT_AVG_SPEED_KMH) * 60.0

    # Return (list of labels in order, distance_km, est_time_min)
    return optimized_names, round(total_distance_km, 3), round(estimated_time_min, 2)
