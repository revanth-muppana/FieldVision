# 🏈 FieldVision: Weather Risk Analyzer

**FieldVision** is a full-stack data engineering application that analyzes real-time weather data to predict game-day risks for NFL stadiums.

Deployed Live: [https://fieldvision-7de9e6568b96.herokuapp.com/](https://fieldvision-7de9e6568b96.herokuapp.com/)

## Architecture
This project follows a microservices-inspired architecture with a clear separation of concerns:

1.  **Data Collector (`src/collector`):** A background worker that fetches 5-day forecasts for 30 NFL stadiums using the OpenWeatherMap API.
2.  **Database:** * **Local:** SQLite for rapid development.
    * **Production:** Heroku Postgres for persistent cloud storage.
3.  **Analyzer (`src/analyzer`):** A logic engine that processes raw weather JSON to calculate a "Risk Score" (0-100) based on wind speed and temperature.
4.  **Web Application (`src/app.py`):** A Flask-based REST API and Dashboard that serves the analyzed data to users.

## Features
* **Automated Data Pipeline:** Fetches and processes data automatically.
* **Dual-Database Support:** Seamlessly switches between SQLite (Dev) and Postgres (Prod).
* **Risk Algorithm:** Custom logic to flag "High Risk" games based on wind and freeze conditions.
* **CI/CD:** GitHub Actions automatically runs Unit & Integration tests on every push.

## Tech Stack
* **Language:** Python 3.9
* **Framework:** Flask
* **Database:** PostgreSQL / SQLite
* **Deployment:** Heroku
* **Tools:** Gunicorn, Pytest, GitHub Actions

## How to Run Locally

### 1. Installation
```bash
# Clone the repo
git clone [https://github.com/revanth-muppana/FieldVision.git](https://github.com/revanth-muppana/FieldVision.git)
cd fieldvision

# Create virtual env
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt