from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from tsp_basic import solve_tsp as basic_tsp
from tsp_modified import solve_tsp as optimized_tsp

import os, requests
from tsp_basic import solve_tsp as basic_tsp
from tsp_modified import solve_tsp as optimized_tsp

from algos import tsp_bruteforce
from route_optimiser import summarize_route

# Load environment variables
load_dotenv()

app = Flask(__name__)
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")


# ----------------------------- ROUTES ---------------------------------

@app.route('/')
def index():
    return render_template('index.html', opencage_api_key=OPENCAGE_API_KEY)


@app.route('/geocode', methods=['POST'])
def geocode_location():
    data = request.get_json()
    location = data.get('location')

    if not location:
        return jsonify({'error': 'No location provided'}), 400

    try:
        url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={OPENCAGE_API_KEY}"
        res = requests.get(url).json()
        if res.get('results'):
            geo = res['results'][0]['geometry']
            formatted = res['results'][0].get('formatted', location)
            return jsonify({
                'latitude': geo['lat'],
                'longitude': geo['lng'],
                'formatted_address': formatted
            })
        else:
            return jsonify({'error': 'Location not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data received'}), 400

    locations = data.get('locations', [])
    coordinates = data.get('coordinates', {})

    if not locations or not coordinates:
        return jsonify({'error': 'Missing locations or coordinates'}), 400

    try:
        optimized_path, total_distance_km, total_time_min = tsp_bruteforce(locations, coordinates)
        response = summarize_route(
            optimized_path=optimized_path,
            total_distance=round(total_distance_km, 2),
            estimated_time=round(total_time_min, 2)
        )
        response["route_coordinates"] = [
            coordinates[city] for city in optimized_path if city in coordinates
        ]
        return jsonify(response)

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({'error': f'Route optimization failed: {str(e)}'}), 500


# ----------------------------- NEW /tsp ROUTE ---------------------------------

@app.route("/tsp", methods=["POST"])
def run_tsp():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload received"}), 400

    locations = data.get("locations", [])
    coordinates = data.get("coordinates", {})
    mode = data.get("mode", "basic")  # "basic" or "optimized"

    if not locations or not coordinates:
        return jsonify({"error": "Missing 'locations' or 'coordinates' in payload"}), 400

    try:
        if mode == "optimized":
            route, distance_km, estimated_time_min = optimized_tsp(locations, coordinates)
        else:
            route, distance_km, estimated_time_min = basic_tsp(locations, coordinates)

        return jsonify({
            "route": route,
            "total_distance_km": distance_km,
            "estimated_time_min": estimated_time_min,
            "mode_used": mode
        })

    except Exception as e:
        print("❌ /tsp ERROR:", str(e))
        return jsonify({"error": f"TSP computation failed: {str(e)}"}), 500


# ----------------------------- MAIN ---------------------------------

if __name__ == '__main__':
    app.run(debug=True)
