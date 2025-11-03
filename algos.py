import math
import itertools

# ---------------------------------------------------------------
# 🧮 Euclidean Distance
# ---------------------------------------------------------------
def euclidean_distance(coord1, coord2):
    """Calculate Euclidean distance (in km) between two points."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # Rough km scaling


# ---------------------------------------------------------------
# 🗺️ Basic TSP (Brute Force)
# ---------------------------------------------------------------
def basic_tsp(locations, coordinates):
    """
    Basic Traveling Salesman Problem solver using brute force.
    Tries all permutations and finds the minimum total distance.
    """
    print("\n🚀 Running Basic TSP (Brute Force)...")

    n = len(locations)
    if n <= 1:
        return locations, 0.0, 0.0

    min_distance = float('inf')
    best_path = None

    # Try all possible routes starting from first location
    start = locations[0]
    other_locations = locations[1:]

    for perm in itertools.permutations(other_locations):
        route = [start] + list(perm) + [start]  # return to start
        total_distance = 0

        for i in range(len(route) - 1):
            loc1, loc2 = route[i], route[i + 1]
            if loc1 in coordinates and loc2 in coordinates:
                total_distance += euclidean_distance(coordinates[loc1], coordinates[loc2])
            else:
                total_distance = float('inf')
                break

        if total_distance < min_distance:
            min_distance = total_distance
            best_path = route

    # Estimate travel time (assuming average 40 km/h)
    avg_speed_kmh = 40
    estimated_time_hr = min_distance / avg_speed_kmh if min_distance != float('inf') else 0


    return best_path, round(min_distance, 2), round(estimated_time_hr, 2)

    
