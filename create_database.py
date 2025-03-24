import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect('flight_database.db')
cursor = conn.cursor()

# Create Airports table with more fields
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Airports (
        airport_id INTEGER PRIMARY KEY AUTOINCREMENT,
        iata_code TEXT UNIQUE NOT NULL,
        icao_code TEXT UNIQUE,
        name TEXT NOT NULL,
        city TEXT,
        country TEXT,
        latitude REAL,
        longitude REAL,
        timezone TEXT,
        terminal TEXT,
        gate TEXT
    )
''')

# Create Airlines table with additional details
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Airlines (
        airline_id INTEGER PRIMARY KEY AUTOINCREMENT,
        iata_code TEXT UNIQUE NOT NULL,
        icao_code TEXT UNIQUE,
        name TEXT NOT NULL,
        country TEXT
    )
''')

# Create Flights table for richer API data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Flights (
        flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_iata TEXT UNIQUE NOT NULL,
        flight_icao TEXT,
        airline_id INTEGER,
        departure_airport_id INTEGER,
        arrival_airport_id INTEGER,
        scheduled_departure TEXT,
        scheduled_arrival TEXT,
        actual_departure TEXT,
        actual_arrival TEXT,
        status TEXT,
        delay_minutes INTEGER DEFAULT 0,
        aircraft_type TEXT,
        departure_gate TEXT,
        arrival_gate TEXT,
        FOREIGN KEY (airline_id) REFERENCES Airlines(airline_id),
        FOREIGN KEY (departure_airport_id) REFERENCES Airports(airport_id),
        FOREIGN KEY (arrival_airport_id) REFERENCES Airports(airport_id)
    )
''')

# Commit changes and close
conn.commit()
conn.close()

print("Database and tables created successfully!")