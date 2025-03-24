-- Airports table
CREATE TABLE Airports (
    airport_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    iata_code CHAR(3) UNIQUE,
    icao_code CHAR(4) UNIQUE,
    country VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);

-- Airlines table
CREATE TABLE Airlines (
    airline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Flights table
CREATE TABLE Flights (
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
);

-- Insert 10 European airports
INSERT INTO Airports (name, iata_code, icao_code, country, city, latitude, longitude) VALUES
('Berlin Brandenburg', 'BER', 'EDDB', 'Germany', 'Berlin', 52.3514, 13.4937),
('Munich Airport', 'MUC', 'EDDM', 'Germany', 'Munich', 48.3538, 11.7861),
('Frankfurt Airport', 'FRA', 'EDDF', 'Germany', 'Frankfurt', 50.0333, 8.5706),
('Hamburg Airport', 'HAM', 'EDDH', 'Germany', 'Hamburg', 53.6304, 9.9882),
('Cologne Bonn Airport', 'CGN', 'EDDK', 'Germany', 'Cologne', 50.8659, 7.1427),
('Paris Charles de Gaulle', 'CDG', 'LFPG', 'France', 'Paris', 49.0097, 2.5479),
('Amsterdam Schiphol', 'AMS', 'EHAM', 'Netherlands', 'Amsterdam', 52.3086, 4.7639),
('London Heathrow', 'LHR', 'EGLL', 'United Kingdom', 'London', 51.4700, -0.4543),
('Madrid-Barajas', 'MAD', 'LEMD', 'Spain', 'Madrid', 40.4936, -3.5668),
('Stockholm Arlanda', 'ARN', 'ESSA', 'Sweden', 'Stockholm', 59.6519, 17.9186);

-- Insert 5 airlines
INSERT INTO Airlines (name) VALUES
('Lufthansa'),
('Eurowings'),
('Air France'),
('British Airways'),
('KLM');

-- Insert 20 flights
INSERT INTO Flights (flight_iata, departure_airport_id, arrival_airport_id, airline_id, scheduled_departure, scheduled_arrival, actual_departure, actual_arrival, delay_minutes, status) VALUES
('LH123', 1, 2, 1, '2025-03-24 08:00:00', '2025-03-24 09:30:00', '2025-03-24 08:00:00', '2025-03-24 09:30:00', 0, 'landed'),
('EW456', 2, 3, 2, '2025-03-24 10:00:00', '2025-03-24 11:15:00', '2025-03-24 12:30:00', '2025-03-24 13:45:00', 150, 'landed'),
('LH789', 3, 4, 1, '2025-03-24 12:00:00', '2025-03-24 13:00:00', '2025-03-24 12:00:00', '2025-03-24 13:00:00', 0, 'scheduled'),
('EW101', 4, 5, 2, '2025-03-24 14:00:00', '2025-03-24 15:00:00', '2025-03-24 16:30:00', '2025-03-24 17:30:00', 150, 'active'),
('LH202', 5, 1, 1, '2025-03-24 16:00:00', '2025-03-24 17:30:00', NULL, NULL, 0, 'scheduled'),
('EW303', 1, 3, 2, '2025-03-24 18:00:00', '2025-03-24 19:15:00', '2025-03-24 20:45:00', '2025-03-24 22:00:00', 165, 'landed'),
('LH404', 2, 4, 1, '2025-03-24 20:00:00', '2025-03-24 21:00:00', '2025-03-24 20:00:00', '2025-03-24 21:00:00', 0, 'scheduled'),
('EW505', 3, 5, 2, '2025-03-24 22:00:00', '2025-03-24 23:00:00', '2025-03-25 00:30:00', '2025-03-25 01:30:00', 150, 'active'),
('LH606', 4, 1, 1, '2025-03-24 09:00:00', '2025-03-24 10:30:00', '2025-03-24 09:00:00', '2025-03-24 10:30:00', 0, 'landed'),
('EW707', 5, 2, 2, '2025-03-24 11:00:00', '2025-03-24 12:15:00', '2025-03-24 14:00:00', '2025-03-24 15:15:00', 180, 'landed'),
('AF108', 6, 8, 3, '2025-03-24 07:30:00', '2025-03-24 09:00:00', '2025-03-24 07:30:00', '2025-03-24 09:00:00', 0, 'landed'),
('BA456', 8, 9, 4, '2025-03-24 09:45:00', '2025-03-24 11:30:00', '2025-03-24 11:00:00', '2025-03-24 12:45:00', 75, 'landed'),
('KL789', 7, 6, 5, '2025-03-24 13:00:00', '2025-03-24 14:15:00', '2025-03-24 15:30:00', '2025-03-24 16:45:00', 150, 'active'),
('LH910', 3, 7, 1, '2025-03-24 15:00:00', '2025-03-24 16:30:00', NULL, NULL, 0, 'scheduled'),
('EW111', 5, 10, 2, '2025-03-24 17:00:00', '2025-03-24 19:00:00', '2025-03-24 20:00:00', '2025-03-24 22:00:00', 180, 'landed'),
('AF222', 6, 9, 3, '2025-03-24 19:30:00', '2025-03-24 21:15:00', '2025-03-24 19:30:00', '2025-03-24 21:15:00', 0, 'scheduled'),
('BA333', 8, 1, 4, '2025-03-24 21:00:00', '2025-03-24 23:00:00', '2025-03-24 23:30:00', '2025-03-25 01:30:00', 150, 'active'),
('KL444', 7, 10, 5, '2025-03-25 08:00:00', '2025-03-25 10:00:00', '2025-03-25 08:00:00', '2025-03-25 10:00:00', 0, 'landed'),
('LH555', 2, 6, 1, '2025-03-25 10:30:00', '2025-03-25 12:00:00', '2025-03-25 13:00:00', '2025-03-25 14:30:00', 150, 'landed'),
('EW666', 10, 4, 2, '2025-03-25 12:00:00', '2025-03-25 14:00:00', NULL, NULL, 0, 'scheduled');

-- Queries
-- Flights from a specific airport (e.g., FRA)
SELECT f.flight_iata, a1.name AS departure, a2.name AS arrival, f.scheduled_departure, f.status, f.delay_minutes
FROM Flights f
JOIN Airports a1 ON f.departure_airport_id = a1.airport_id
JOIN Airports a2 ON f.arrival_airport_id = a2.airport_id
WHERE a1.iata_code = 'FRA';

-- Flights delayed > 2 hours
SELECT f.flight_iata, a1.name AS departure, a2.name AS arrival, f.delay_minutes, f.status
FROM Flights f
JOIN Airports a1 ON f.departure_airport_id = a1.airport_id
JOIN Airports a2 ON f.arrival_airport_id = a2.airport_id
WHERE f.delay_minutes > 120;

-- Flight details by flight number (e.g., EW456)
SELECT f.flight_iata, a1.name AS departure, a2.name AS arrival, al.name AS airline, f.scheduled_departure, f.actual_departure, f.status, f.delay_minutes
FROM Flights f
JOIN Airports a1 ON f.departure_airport_id = a1.airport_id
JOIN Airports a2 ON f.arrival_airport_id = a2.airport_id
JOIN Airlines al ON f.airline_id = al.airline_id
WHERE f.flight_iata = 'EW456';

-- Additional Queries
-- All flights by Lufthansa
SELECT f.flight_iata, a1.name AS departure, a2.name AS arrival, f.delay_minutes, f.status
FROM Flights f
JOIN Airports a1 ON f.departure_airport_id = a1.airport_id
JOIN Airports a2 ON f.arrival_airport_id = a2.airport_id
JOIN Airlines al ON f.airline_id = al.airline_id
WHERE al.name = 'Lufthansa';

-- Flights departing from France
SELECT f.flight_iata, a1.name AS departure, a2.name AS arrival, f.scheduled_departure, f.status
FROM Flights f
JOIN Airports a1 ON f.departure_airport_id = a1.airport_id
JOIN Airports a2 ON f.arrival_airport_id = a2.airport_id
WHERE a1.country = 'France';