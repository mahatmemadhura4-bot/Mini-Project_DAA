
---

```markdown
# 🧭 Smart Route Optimizer

## 🚀 Overview
**Smart Route Optimizer** is a web-based Flask application that helps users find the most efficient route between multiple locations.  
It uses the **OpenCage Geocoding API** to convert place names into latitude and longitude coordinates and applies a **Modified TSP (Travelling Salesman Problem)** logic to generate the optimal route.

---

## ⚙️ Installation and Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Kimaya0310/Mini-Projects.git
cd smart-route-optimizer
````

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate     # For Windows
# OR
source venv/bin/activate  # For Mac/Linux
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Create a `.env` File

Inside the root folder, create a file named `.env` and add:

```
SECRET_KEY=your_flask_secret_key
OPENCAGE_API_KEY=your_opencage_api_key
```

You can get a free OpenCage API key here:
👉 [https://opencagedata.com/api](https://opencagedata.com/api)

---

## 🧠 How It Works

### 🗺️ Geocoding

* The app sends a location name (like “Pune, India”) to the **OpenCage API**.
* The API returns latitude and longitude coordinates.

### ♻️ Route Optimization

* The app uses a **Modified Travelling Salesman Problem (TSP)** approach to optimize routes between multiple locations.
* You can customize the logic in `route_model.py` and `route_optimiser.py`.

---

## 🧩 API Endpoints

### 1. `/geocode` (POST)

Converts a location name into latitude and longitude.
**Request:**

```json
{
  "location": "Pune, India"
}
```

**Response:**

```json
{
  "latitude": 18.5204,
  "longitude": 73.8567
}
```

### 2. `/optimize` (POST)

Optimizes the order of travel between multiple points.
**Request:**

```json
{
  "locations": ["Pune", "Mumbai", "Nashik"]
}
```

**Response:**

```json
{
  "optimized_route": ["Pune", "Nashik", "Mumbai"],
  "message": "Route optimized successfully"
}
```

---

## 💻 Running the App

Start the Flask development server:

```bash
python app.py
```

Then open your browser and visit:
👉 `http://127.0.0.1:5000/`

---

## 📦 Technologies Used

* **Flask** – Web framework
* **Python 3.x** – Core programming language
* **OpenCage Geocoding API** – For location-to-coordinate conversion
* **HTML / CSS** – Frontend templates
* **dotenv** – Environment variable management

---

## 🧠 Future Enhancements

* Add real-time distance matrix (using Google Maps or OSRM API)
* Implement Dijkstra or A* for better route optimization
* Add user authentication & route history
* Visualize optimized route using Leaflet or Mapbox

---

## 🧑‍💻 Author

**Developed by:** Kimaya