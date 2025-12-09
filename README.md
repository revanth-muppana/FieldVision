# 🏈 FieldVision: Weather Risk Analyzer

**FieldVision** is a full-stack data engineering application that analyzes real-time weather data to predict game-day risks for NFL stadiums.

Deployed Live: [https://fieldvision-7de9e6568b96.herokuapp.com/](https://fieldvision-7de9e6568b96.herokuapp.com/)

## Architecture
This project follows a microservices-inspired architecture with a clear separation of concerns:

1.  **Data Collector (`src/collector/collector.py`):** A background worker that fetches 5-day forecasts for 30 NFL stadiums using the OpenWeatherMap API.
2.  **Database:**
    * **Local:** SQLite for rapid development.
    * **Production:** Heroku Postgres for persistent cloud storage.
4.  **Analyzer (`src/analyzer/analyzer.py`):** A logic engine that processes raw weather JSON to calculate a "Risk Score" (0-100) based on wind speed and temperature.
5.  **Web Application (`src/app.py`):** A Flask-based REST API and Dashboard that serves the analyzed data to users.

## Features
* **Automated Data Pipeline:** Fetches and processes data automatically.
* **Dual-Database Support:** Seamlessly switches between SQLite (Dev) and Postgres (Prod).
* **Risk Algorithm:** Custom logic to flag "High Risk" games based on wind and freeze conditions.
* **CI/CD:** GitHub Actions automatically runs Unit & Integration tests on every push.

## Tech Stack
* **Language:** Python 3.10
* **Framework:** Flask
* **Database:** PostgreSQL / SQLite
* **Deployment:** Heroku
* **Tools:** Gunicorn, Pytest, GitHub Actions

## How to Run Locally

### 1. Installation
```bash
# Clone the repo
git clone https://github.com/revanth-muppana/FieldVision.git
cd fieldvision

# Create virtual env
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Pipeline
```bash
# Set path
export PYTHONPATH=src

# Step 1: Collect Data (Fetches fresh weather)
python src/collector/collector.py

# Step 2: Analyze Data (Calculates Risk Scores)
python src/analyzer/analyzer.py

# Step 3: Launch Website
python src/app.py

Visit http://127.0.0.1:5000 to see the dashboard.
```

### 3. Testing
```bash
# Run Unit Tests (Logic checks)
python src/tests/unit_test.py

# Run Integration Tests (Full pipeline verification)
python src/tests/integration_test.py
```
