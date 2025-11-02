import math
import itertools

# ---------------------------------------------------------------
# 🧩 Distance Matrix Construction
# ---------------------------------------------------------------
def create_distance_matrix(locations, coordinates):
    """Create a 2D distance matrix (in km) for all given locations."""
    n = len(locations)
    dist_matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j:
                loc_i, loc_j = locations[i], locations[j]
                if loc_i in coordinates and loc_j in coordinates:
                    dist_matrix[i][j] = euclidean_distance(coordinates[loc_i], coordinates[loc_j])
                else:
                    dist_matrix[i][j] = float('inf')
    return dist_matrix


# ---------------------------------------------------------------
# 🌲 Prim’s Minimum Spanning Tree (MST)
# ---------------------------------------------------------------
def prim_mst(distance_matrix):
    """Compute MST using Prim's algorithm and return parent[] array."""
    n = len(distance_matrix)
    key = [float('inf')] * n
    parent = [-1] * n
    mst_set = [False] * n

    key[0] = 0  # start from node 0

    for _ in range(n):
        u = min((key[i], i) for i in range(n) if not mst_set[i])[1]
        mst_set[u] = True

        for v in range(n):
            if distance_matrix[u][v] > 0 and not mst_set[v] and distance_matrix[u][v] < key[v]:
                key[v] = distance_matrix[u][v]
                parent[v] = u
    return parent


# ---------------------------------------------------------------
# 🔁 Preorder DFS Traversal (MST → TSP Approximation)
# ---------------------------------------------------------------
def preorder_traversal_mst(parent):
    """Generate preorder traversal (DFS) from MST to approximate TSP."""
    n = len(parent)
    adj = [[] for _ in range(n)]

    for i in range(1, n):
        if parent[i] != -1:
            adj[parent[i]].append(i)
            adj[i].append(parent[i])

    visited = [False] * n
    order = []

    def dfs(u):
        visited[u] = True
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                dfs(v)

    dfs(0)
    order.append(0)  # return to start
    return order


# ---------------------------------------------------------------
# 📏 Total Distance Calculation
# ---------------------------------------------------------------
def calculate_total_distance(order, distance_matrix):
    """Calculate total travel distance for a given route order (in km)."""
    total_distance = 0.0
    for i in range(len(order) - 1):
        d = distance_matrix[order[i]][order[i + 1]]
        if d == float('inf'):
            continue
        total_distance += d
    return total_distance


# ---------------------------------------------------------------
# 🧠 Route Optimization (MST + TSP Hybrid)
# ---------------------------------------------------------------
def find_optimized_route(locations, coordinates):
    """
    Optimize route using Hybrid MST + TSP approximation.
    Returns dictionary suitable for JSON response.
    """
    print("\n🚀 Running Route Optimization...")
    n = len(locations)
    if n <= 1:
        return {
            "optimized_path": locations,
            "total_distance": 0,
            "estimated_time": 0,
            "route_coordinates": [coordinates[loc] for loc in locations if loc in coordinates]
        }

    # Step 1: Create distance matrix
    distance_matrix = create_distance_matrix(locations, coordinates)

    # Step 2: Build MST
    parent = prim_mst(distance_matrix)

    # Step 3: Approximate TSP route using preorder DFS
    tsp_order = preorder_traversal_mst(parent)
    optimized_path = [locations[i] for i in tsp_order]

    # Step 4: Compute total distance & time
    total_distance_km = calculate_total_distance(tsp_order, distance_matrix)
    avg_speed_kmh = 40  # km/h
    estimated_time_hr = total_distance_km / avg_speed_kmh if total_distance_km else 0

    route_coordinates = [coordinates[loc] for loc in optimized_path if loc in coordinates]

    return {
        "optimized_path": optimized_path,
        "total_distance": round(total_distance_km, 2),
        "estimated_time": round(estimated_time_hr, 2),
        "route_coordinates": route_coordinates
    }


def euclidean_distance(coord1, coord2):
    """Calculate Euclidean distance (in km) between two points."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # rough km scaling

def tsp_bruteforce(locations, coordinates):
    """Brute-force TSP using Euclidean distance."""
    min_distance = float('inf')
    best_path = []

    for perm in itertools.permutations(locations):
        distance = 0
        for i in range(len(perm) - 1):
            c1, c2 = coordinates[perm[i]], coordinates[perm[i+1]]
            distance += euclidean_distance(c1, c2)
        if distance < min_distance:
            min_distance = distance
            best_path = perm

    avg_speed = 40  # km/h
    total_time_min = (min_distance / avg_speed) * 60

    return list(best_path), min_distance, total_time_min