import requests
import sqlite3
from datetime import datetime

# API setup
API_KEY = 'efc51b9b35285aaad72c34bc8d5f9b4e'  # Replace with your AviationStack API key
BASE_URL = 'http://api.aviationstack.com/v1/flights'


# Connect to the database
conn = sqlite3.connect('flight_database.db')
cursor = conn.cursor()

# Function to fetch flights from AviationStack
def fetch_flights(offset=0, limit=100):
    params = {
        'access_key': API_KEY,
        'limit': limit,
        'offset': offset,
        'flight_status': 'scheduled'
    }
    response = requests.get(BASE_URL, params=params)
    print(f"API Response Status: {response.status_code}")
    print(f"Raw Response: {response.text[:500]}...")
    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return []

# Insert or update airport data
def insert_airport(airport_data, is_departure=True):
    iata = airport_data.get('iata', 'N/A')
    if not iata or iata == 'N/A':
        print(f"Skipping airport with invalid IATA: {airport_data}")
        return None
    cursor.execute('''
        INSERT OR IGNORE INTO Airports (iata_code, icao_code, name, city, country, latitude, longitude, timezone, terminal, gate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        iata,
        airport_data.get('icao'),
        airport_data.get('airport', 'Unknown'),
        airport_data.get('city'),
        airport_data.get('country'),
        airport_data.get('latitude'),
        airport_data.get('longitude'),
        airport_data.get('timezone'),
        airport_data.get('terminal'),
        airport_data.get('gate') if is_departure else None
    ))
    cursor.execute("SELECT airport_id FROM Airports WHERE iata_code = ?", (iata,))
    result = cursor.fetchone()
    if result:
        return result[0]
    print(f"Failed to fetch airport_id for IATA: {iata}")
    return None

# Insert or update airline data
def insert_airline(airline_data):
    iata = airline_data.get('iata', 'N/A')
    if not iata or iata == 'N/A':
        print(f"Skipping airline with invalid IATA: {airline_data}")
        return None
    cursor.execute('''
        INSERT OR IGNORE INTO Airlines (iata_code, icao_code, name, country)
        VALUES (?, ?, ?, ?)
    ''', (
        iata,
        airline_data.get('icao'),
        airline_data.get('name', 'Unknown'),
        airline_data.get('country')
    ))
    cursor.execute("SELECT airline_id FROM Airlines WHERE iata_code = ?", (iata,))
    result = cursor.fetchone()
    if result:
        return result[0]
    print(f"Failed to fetch airline_id for IATA: {iata}")
    return None

# Insert flight data
def insert_flight(flight):
    airline_id = insert_airline(flight.get('airline', {}))
    dep_id = insert_airport(flight.get('departure', {}), is_departure=True)
    arr_id = insert_airport(flight.get('arrival', {}), is_departure=False)
    flight_iata = flight.get('flight', {}).get('iata', 'N/A')
    if not flight_iata or flight_iata == 'N/A' or not dep_id or not arr_id or not airline_id:
        print(f"Skipping flight due to missing data: {flight_iata}, Airline ID: {airline_id}, Dep ID: {dep_id}, Arr ID: {arr_id}")
        return

    # Calculate delay if possible
    sched_dep = flight.get('departure', {}).get('scheduled')
    actual_dep = flight.get('departure', {}).get('actual')
    delay_minutes = 0
    if sched_dep and actual_dep:
        sched_time = datetime.strptime(sched_dep, '%Y-%m-%dT%H:%M:%S+00:00')
        actual_time = datetime.strptime(actual_dep, '%Y-%m-%dT%H:%M:%S+00:00')
        delay_minutes = int((actual_time - sched_time).total_seconds() / 60)

    # Handle aircraft field safely
    aircraft = flight.get('aircraft')
    aircraft_type = aircraft.get('registration') if aircraft else None

    cursor.execute('''
        INSERT OR IGNORE INTO Flights (
            flight_iata, flight_icao, airline_id, departure_airport_id, arrival_airport_id,
            scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
            status, delay_minutes, aircraft_type, departure_gate, arrival_gate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        flight_iata,
        flight.get('flight', {}).get('icao'),
        airline_id,
        dep_id,
        arr_id,
        flight.get('departure', {}).get('scheduled'),
        flight.get('arrival', {}).get('scheduled'),
        flight.get('departure', {}).get('actual'),
        flight.get('arrival', {}).get('actual'),
        flight.get('flight_status'),
        delay_minutes,
        aircraft_type,
        flight.get('departure', {}).get('gate'),
        flight.get('arrival', {}).get('gate')
    ))

# Fetch and store flights (3 requests, up to 300 flights)
print("Fetching live flight data...")
total_flights = 0
for offset in [0, 100, 200]:
    flights = fetch_flights(offset=offset)
    for flight in flights:
        insert_flight(flight)
        total_flights += 1
    print(f"Fetched {len(flights)} flights at offset {offset}")

# Commit changes
conn.commit()

# Verify counts
cursor.execute("SELECT COUNT(*) FROM Airports")
print(f"Airports stored: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM Airlines")
print(f"Airlines stored: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM Flights")
print(f"Flights stored: {cursor.fetchone()[0]}")

conn.close()
print(f"Total flights processed: {total_flights}")