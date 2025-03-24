from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
import requests
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
import folium
from folium.plugins import MarkerCluster
import plotly
import plotly.graph_objs as go
import json
import uuid

app = Flask(__name__)
Bootstrap(app)

# API Configuration
API_KEY = 'efc51b9b35285aaad72c34bc8d5f9b4e'  # Your AviationStack key
API_BASE_URL = 'http://api.aviationstack.com/v1/flights'
EU_COUNTRIES = ['DE', 'FR', 'IT', 'ES', 'GB', 'PL', 'NL', 'BE', 'SE', 'DK']  # Use 'GB' not 'UK'

# Helper function to fetch flight data from API
def get_flight_data(params=None):
    default_params = {
        'access_key': API_KEY,
        'limit': 50
    }
    if params:
        default_params.update(params)
    try:
        response = requests.get(API_BASE_URL, params=default_params)
        response.raise_for_status()
        data = response.json().get('data', [])
        return data if data else []
    except requests.RequestException as e:
        print(f"API error: {e}")
        return []

# Database setup
def init_db():
    conn = sqlite3.connect('euro_flights.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Airports (
        airport_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        iata_code CHAR(3) UNIQUE,
        icao_code CHAR(4) UNIQUE,
        country VARCHAR(50) NOT NULL,
        city VARCHAR(50) NOT NULL,
        latitude DECIMAL(9,6),
        longitude DECIMAL(9,6)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS Airlines (
        airline_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL UNIQUE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS Flights (
        flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_iata VARCHAR(10) NOT NULL,
        departure_airport_id INTEGER,
        arrival_airport_id INTEGER,
        airline_id INTEGER,
        scheduled_departure DATETIME,
        scheduled_arrival DATETIME,
        actual_departure DATETIME,
        actual_arrival DATETIME,
        delay_minutes INTEGER DEFAULT 0,
        status VARCHAR(20),
        FOREIGN KEY (departure_airport_id) REFERENCES Airports(airport_id),
        FOREIGN KEY (arrival_airport_id) REFERENCES Airports(airport_id),
        FOREIGN KEY (airline_id) REFERENCES Airlines(airline_id)
    )''')
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect('euro_flights.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# Sync API data to database (Europe only)
def sync_flights():
    conn = get_db_connection()
    c = conn.cursor()
    params = {'dep_country': ','.join(EU_COUNTRIES)}
    flights = get_flight_data(params)
    print(f"API returned {len(flights)} flights: {flights[:2]}")
    if not flights:
        print("No flights returned from API. Check API key or limits.")
        return

    european_flights_found = False
    for f in flights:
        dep = f.get('departure', {})
        arr = f.get('arrival', {})
        timezone = dep.get('timezone')  # Might be None
        dep_country = timezone.split('/')[0] if timezone and '/' in timezone else ''
        if dep_country != 'Europe':
            print(f"Skipping non-European flight: {f}")
            continue
        
        european_flights_found = True
        flight_iata = f.get('flight', {}).get('iata') or f.get('flight_iata') or 'UNKNOWN_' + str(uuid.uuid4())[:8]
        if not flight_iata:
            print(f"Skipping flight with no IATA: {f}")
            continue

        dep_iata = dep.get('iata')
        arr_iata = arr.get('iata')
        airline_name = f.get('airline', {}).get('name')

        c.execute("INSERT OR IGNORE INTO Airports (name, iata_code, country, city) VALUES (?, ?, ?, ?)",
                  (dep.get('airport', 'Unknown'), dep_iata, 'Unknown', 'Unknown'))
        c.execute("INSERT OR IGNORE INTO Airports (name, iata_code, country, city) VALUES (?, ?, ?, ?)",
                  (arr.get('airport', 'Unknown'), arr_iata, 'Unknown', 'Unknown'))
        c.execute("INSERT OR IGNORE INTO Airlines (name) VALUES (?)", (airline_name or 'Unknown',))

        dep_id = c.execute("SELECT airport_id FROM Airports WHERE iata_code = ?", (dep_iata,)).fetchone()[0]
        arr_id = c.execute("SELECT airport_id FROM Airports WHERE iata_code = ?", (arr_iata,)).fetchone()[0]
        airline_id = c.execute("SELECT airline_id FROM Airlines WHERE name = ?", (airline_name or 'Unknown',)).fetchone()[0]

        c.execute("INSERT OR REPLACE INTO Flights (flight_iata, departure_airport_id, arrival_airport_id, airline_id, scheduled_departure, scheduled_arrival, actual_departure, actual_arrival, delay_minutes, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (flight_iata, dep_id, arr_id, airline_id, dep.get('scheduled'), arr.get('scheduled'), dep.get('actual'), arr.get('actual'), f.get('departure', {}).get('delay', 0) or 0, f.get('flight_status', 'unknown')))
    
    if not european_flights_found:
        print("No European flights found in API response. Consider using mock data from schema.sql.")
    
    conn.commit()
    conn.close()

scheduler = BackgroundScheduler()
scheduler.add_job(sync_flights, 'interval', minutes=15)
scheduler.start()

# Home page
@app.route('/', methods=['GET', 'POST'])
def index():
    search_flight = request.form.get('search_flight', '').strip()
    filter_dep = request.form.get('filter_dep', '')
    filter_arr = request.form.get('filter_arr', '')
    filter_airline = request.form.get('filter_airline', '')
    filter_status = request.form.get('filter_status', '')

    conn = get_db_connection()
    c = conn.cursor()
    
    query = "SELECT f.flight_iata, a1.name AS dep_airport, a2.name AS arr_airport, f.scheduled_departure, f.status, f.delay_minutes, al.name AS airline FROM Flights f JOIN Airports a1 ON f.departure_airport_id = a1.airport_id JOIN Airports a2 ON f.arrival_airport_id = a2.airport_id JOIN Airlines al ON f.airline_id = al.airline_id WHERE 1=1"
    params = []
    
    if search_flight:
        query += " AND f.flight_iata = ?"
        params.append(search_flight)
    if filter_dep:
        query += " AND a1.iata_code = ?"
        params.append(filter_dep)
    if filter_arr:
        query += " AND a2.iata_code = ?"
        params.append(filter_arr)
    if filter_airline:
        query += " AND al.name = ?"
        params.append(filter_airline)
    if filter_status:
        query += " AND f.status = ?"
        params.append(filter_status.lower())
    
    query += " LIMIT 50"
    c.execute(query, params)
    flights = c.fetchall()
    
    c.execute("SELECT DISTINCT iata_code FROM Airports WHERE country IN ({})".format(','.join('?'*len(EU_COUNTRIES))), EU_COUNTRIES)
    airports = sorted(row['iata_code'] for row in c.fetchall() if row['iata_code'])
    c.execute("SELECT DISTINCT name FROM Airlines")
    airlines = sorted(row['name'] for row in c.fetchall() if row['name'])
    statuses = ['scheduled', 'active', 'landed', 'cancelled']
    c.execute("SELECT COUNT(*) FROM Flights")
    total_flights = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM Airports WHERE country IN ({})".format(','.join('?'*len(EU_COUNTRIES))), EU_COUNTRIES)
    total_airports = c.fetchone()[0]
    
    conn.close()
    
    return render_template('index.html', flights=flights, airports=airports, airlines=airlines,
                           statuses=statuses, total_flights=total_flights, total_airports=total_airports,
                           search_flight=search_flight, filter_dep=filter_dep, filter_arr=filter_arr,
                           filter_airline=filter_airline, filter_status=filter_status)

# Flight Map page
@app.route('/map', methods=['GET', 'POST'])
def flight_map():
    filter_region = request.form.get('filter_region', 'All')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    query = "SELECT f.flight_iata, a1.name AS dep_airport, a1.latitude AS dep_lat, a1.longitude AS dep_lon, a2.name AS arr_airport, a2.latitude AS arr_lat, a2.longitude AS arr_lon, f.status FROM Flights f JOIN Airports a1 ON f.departure_airport_id = a1.airport_id JOIN Airports a2 ON f.arrival_airport_id = a2.airport_id"
    params = []
    if filter_region != 'All':
        query += " WHERE a1.country = ?"
        params.append(filter_region)
    
    query += " LIMIT 50"
    c.execute(query, params)
    flights = c.fetchall()
    
    c.execute("SELECT DISTINCT country FROM Airports WHERE country IN ({})".format(','.join('?'*len(EU_COUNTRIES))), EU_COUNTRIES)
    regions = ['All'] + sorted(row['country'] for row in c.fetchall() if row['country'])
    
    conn.close()
    
    flight_map = folium.Map(location=[50, 10], zoom_start=4, tiles='cartodbpositron')  # Center on Europe
    marker_cluster = MarkerCluster().add_to(flight_map)
    
    if not flights:
        folium.Marker(location=[0, 0], popup="No flights found for this region", icon=folium.Icon(color='gray')).add_to(flight_map)
    else:
        bounds = []
        for flight in flights:
            if flight['dep_lat'] and flight['dep_lon'] and flight['arr_lat'] and flight['arr_lon']:
                dep_coords = [float(flight['dep_lat']), float(flight['dep_lon'])]
                arr_coords = [float(flight['arr_lat']), float(flight['arr_lon'])]
                popup_text = f"{flight['flight_iata']}: {flight['dep_airport']} to {flight['arr_airport']} ({flight['status']})"
                folium.Marker(dep_coords, popup=popup_text, icon=folium.Icon(color='blue')).add_to(marker_cluster)
                folium.Marker(arr_coords, popup=popup_text, icon=folium.Icon(color='green')).add_to(marker_cluster)
                folium.PolyLine([dep_coords, arr_coords], color="blue", weight=1.5, opacity=0.7, dash_array='5').add_to(flight_map)
                bounds.extend([dep_coords, arr_coords])
        
        if bounds:
            flight_map.fit_bounds(bounds)
    
    map_html = flight_map._repr_html_()
    return render_template('map.html', map_html=map_html, regions=regions, filter_region=filter_region, flights=flights)

# Delay Dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    sort_order = request.form.get('sort_order', 'desc')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT f.flight_iata, f.delay_minutes, a1.name AS dep_airport, a2.name AS arr_airport, f.status FROM Flights f JOIN Airports a1 ON f.departure_airport_id = a1.airport_id JOIN Airports a2 ON f.arrival_airport_id = a2.airport_id WHERE f.delay_minutes > 120")
    delayed_flights = c.fetchall()
    total_delayed = len(delayed_flights)
    avg_delay = round(sum(f['delay_minutes'] for f in delayed_flights) / total_delayed, 2) if total_delayed else 0
    
    c.execute("SELECT al.name AS airline, AVG(f.delay_minutes) AS avg_delay FROM Flights f JOIN Airlines al ON f.airline_id = al.airline_id WHERE f.delay_minutes > 0 GROUP BY al.name ORDER BY avg_delay " + ("DESC" if sort_order == 'desc' else "ASC") + " LIMIT 10")
    delay_data = c.fetchall()
    
    c.execute("SELECT COUNT(*) FROM Flights WHERE delay_minutes > 0")
    delayed = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM Flights")
    total = c.fetchone()[0]
    on_time = total - delayed
    
    c.execute("SELECT a.name FROM Flights f JOIN Airports a ON f.departure_airport_id = a.airport_id WHERE f.delay_minutes > 0 GROUP BY a.name ORDER BY AVG(f.delay_minutes) DESC LIMIT 1")
    worst_airport_result = c.fetchone()
    worst_airport = worst_airport_result[0] if worst_airport_result else 'N/A'
    
    conn.close()
    
    bar_fig = go.Figure(data=[go.Bar(
        x=[d['airline'] for d in delay_data],
        y=[d['avg_delay'] for d in delay_data],
        marker_color='#007bff',
        text=[f"{y:.1f}" for y in [d['avg_delay'] for d in delay_data]],
        textposition='auto'
    )])
    bar_fig.update_layout(
        title="Average Delay by Airline (Top 10)",
        xaxis_title="Airline",
        yaxis_title="Avg Delay (min)",
        template="plotly_white",
        font=dict(size=12)
    )
    pie_fig = go.Figure(data=[go.Pie(
        labels=['Delayed', 'On-Time'],
        values=[delayed, on_time],
        hole=.4,
        marker=dict(colors=['#dc3545', '#28a745'])
    )])
    pie_fig.update_layout(
        title="Flight Delay Distribution",
        template="plotly_white",
        font=dict(size=12)
    )
    
    bar_div = plotly.offline.plot(bar_fig, output_type='div', include_plotlyjs=False)
    pie_div = plotly.offline.plot(pie_fig, output_type='div', include_plotlyjs=False)
    
    return render_template('dashboard.html', bar_div=bar_div, pie_div=pie_div, total_delayed=total_delayed,
                           avg_delay=avg_delay, worst_airport=worst_airport, sort_order=sort_order, delayed_flights=delayed_flights)

# Flight Details page
@app.route('/details/<flight_iata>')
def flight_details(flight_iata):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT f.flight_iata, f.scheduled_departure, f.scheduled_arrival, f.actual_departure, f.actual_arrival, 
               f.delay_minutes, f.status, a1.name AS dep_airport, a1.iata_code AS dep_iata, a1.city AS dep_city, 
               a1.country AS dep_country, a1.latitude AS dep_lat, a1.longitude AS dep_lon,
               a2.name AS arr_airport, a2.iata_code AS arr_iata, a2.city AS arr_city, a2.country AS arr_country, 
               a2.latitude AS arr_lat, a2.longitude AS arr_lon, al.name AS airline
        FROM Flights f 
        JOIN Airports a1 ON f.departure_airport_id = a1.airport_id 
        JOIN Airports a2 ON f.arrival_airport_id = a2.airport_id 
        JOIN Airlines al ON f.airline_id = al.airline_id 
        WHERE f.flight_iata = ?
    """, (flight_iata,))
    flight = c.fetchone()
    conn.close()
    
    if not flight:
        return render_template('details.html', error=f"Flight {flight_iata} not found", flight=None, map_html="")
    
    formatted_flight = dict(flight)
    formatted_flight['departure_gate'] = 'N/A'  # Free tier lacks this
    formatted_flight['arrival_gate'] = 'N/A'
    formatted_flight['aircraft_type'] = 'N/A'
    
    if flight['dep_lat'] and flight['dep_lon'] and flight['arr_lat'] and flight['arr_lon']:
        dep_coords = [float(flight['dep_lat']), float(flight['dep_lon'])]
        arr_coords = [float(flight['arr_lat']), float(flight['arr_lon'])]
        mid_point = [(dep_coords[0] + arr_coords[0]) / 2, (dep_coords[1] + arr_coords[1]) / 2]
        mini_map = folium.Map(location=mid_point, zoom_start=4, tiles='cartodbpositron')
        folium.Marker(dep_coords, popup=f"{flight['dep_airport']} ({flight['dep_iata']})", icon=folium.Icon(color='blue')).add_to(mini_map)
        folium.Marker(arr_coords, popup=f"{flight['arr_airport']} ({flight['arr_iata']})", icon=folium.Icon(color='green')).add_to(mini_map)
        folium.PolyLine([dep_coords, arr_coords], color="blue", weight=2, opacity=0.8, dash_array='5').add_to(mini_map)
        map_html = mini_map._repr_html_()
    else:
        map_html = "<div class='text-muted p-3'>Route map unavailable (missing coordinates)</div>"
    
    return render_template('details.html', flight=formatted_flight, map_html=map_html)

# Custom API endpoints
@app.route('/api/flights', methods=['GET'])
def api_flights():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT f.flight_iata, a1.name AS dep, a2.name AS arr, f.delay_minutes FROM Flights f JOIN Airports a1 ON f.departure_airport_id = a1.airport_id JOIN Airports a2 ON f.arrival_airport_id = a2.airport_id")
    flights = [{'flight_iata': row['flight_iata'], 'departure': row['dep'], 'arrival': row['arr'], 'delay': row['delay_minutes']} for row in c.fetchall()]
    conn.close()
    return jsonify(flights)

@app.route('/api/delays', methods=['GET'])
def api_delays():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT f.flight_iata, a1.name AS dep, a2.name AS arr, f.delay_minutes FROM Flights f JOIN Airports a1 ON f.departure_airport_id = a1.airport_id JOIN Airports a2 ON f.arrival_airport_id = a2.airport_id WHERE f.delay_minutes > 120")
    delays = [{'flight_iata': row['flight_iata'], 'departure': row['dep'], 'arrival': row['arr'], 'delay': row['delay_minutes']} for row in c.fetchall()]
    conn.close()
    return jsonify(delays)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)