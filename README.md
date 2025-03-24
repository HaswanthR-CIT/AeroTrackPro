
# AeroTrackPro - Track Flights Across Europe ✈️🌍

## Flask-Based Flight Monitoring System

### Overview

AeroTrackPro is a web application designed to monitor and analyze real-time flight data across Europe. Built with Flask and powered by the AviationStack API, it provides users with an interactive interface to track flight statuses, visualize flight routes on a map, and analyze delay statistics. The app syncs flight data into an SQLite database and includes features like filtering, detailed flight views, and a delay dashboard.

### Features

- **Flight List**: Displays a searchable, filterable list of flights with details like departure, arrival, and status.
- **Interactive Map**: Visualizes flight routes across Europe using Folium.
- **Delay Dashboard**: Shows delay statistics, including average delays by airline and a pie chart of delayed vs. on-time flights.
- **Flight Details**: Provides in-depth info for individual flights with a mini route map.
- **API Integration**: Syncs real-time data from AviationStack every 15 minutes.
- **Mock Data Support**: Includes a fallback `schema.sql` for demo purposes.
- **Custom API Endpoints**: Offers JSON endpoints for flights and delays.

### Tech Stack

- **Python**: Core programming language
- **Flask**: Web framework for UI and backend
- **Flask-Bootstrap**: Styling for the web interface
- **SQLite**: Lightweight database for storing flight data
- **Requests**: API calls to AviationStack
- **Folium**: Interactive maps for flight routes
- **Plotly**: Visualization for delay charts
- **APScheduler**: Background task scheduling for data sync
- **AviationStack API**: Real-time flight data source

### Project Structure

```bash
📂 AeroTrackPro
│── 📂 static/                  # Static assets (CSS, images)
│   │── 📂 css/                # Custom styles
│   │   ├── styles.css         # CSS for UI
│── 📂 templates/              # HTML templates
│   │── index.html            # Home page (flight list)
│   │── map.html              # Flight map page
│   │── dashboard.html        # Delay dashboard
│   │── details.html          # Flight details page
│   │── base.html             # Base template with Bootstrap
│── app.py                    # Main Flask application
│── schema.sql                # Mock data for SQLite DB
│── euro_flights.db           # SQLite database (generated)
│── requirements.txt          # Python dependencies
│── README.md                 # Project documentation
│── .gitignore                # Git ignore file
```

### Data Sync Process

- **API Sync**: Fetches real-time flight data from AviationStack using country codes (e.g., DE, FR, GB).
- **Filtering**: Limits data to European flights based on departure timezone (e.g., Europe/...).
- **Database Storage**: Inserts flights, airports, and airlines into `euro_flights.db` with foreign key relationships.
- **Scheduling**: Runs every 15 minutes via APScheduler.
- **Mock Data**: Optional `schema.sql` loads 20 European flights for testing if API data is unavailable.

### Flask Web App Workflow

- **Home Page**: Users view a list of flights, filter by IATA code, airline, or status, and search by flight number.
- **Map Page**: Displays flight routes on an interactive map, filterable by country.
- **Dashboard**: Shows delay stats (flights > 2 hours delayed in red) with bar and pie charts.
- **Details Page**: Clicking a flight shows its full details and a mini route map.
- **API Endpoints**: `/api/flights` and `/api/delays` return JSON data.

### Setup & Installation

#### Clone the Repository

```bash
git clone https://github.com/[YourUsername]/AeroTrackPro
cd AeroTrackPro
```

#### Set Up Virtual Environment

```bash
python -m venv venv
.env\Scriptsctivate  # Windows
source venv/bin/activate  # Mac/Linux
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Initialize Database

For mock data (recommended for demo):

```bash
sqlite3 euro_flights.db < schema.sql
```

For live data, skip this step and let the API sync run.

#### Run Flask Application

```bash
python app.py
```

Open your browser and visit: `http://localhost:5000/`

### Notes

- **API Limitations**: The free AviationStack tier (100 requests/month) may not always return European flights despite `dep_country` filters. Use `schema.sql` for consistent demo data.
- **Coordinates**: Mock data includes latitude/longitude for maps; live API data may lack these in the free tier.

### License

This project is open-source and available under the MIT License.

```markdown
MIT License

Copyright (c) 2025 [Haswanth R]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
