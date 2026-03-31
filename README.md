# Intelligent Traffic Management System

A Django-based web application to monitor and manage urban traffic signals, vehicle flow, incidents, and analytics in real-time.

## Features
- Real-time signal phase control (RED/GREEN/YELLOW)
- Vehicle count tracking with congestion classification
- Incident reporting and resolution workflow
- Hourly analytics with Chart.js visualizations
- REST API for all core data
- Built-in traffic simulation engine (no external APIs required)
- Role-based access (staff vs regular users)

## Quick Start
```bash
git clone <repo>
cd traffic_management
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000 — log in and click "Seed Demo Data" to populate.

## API Endpoints
- GET /api/stats/ — dashboard summary
- GET/POST /api/intersections/ — intersection management
- GET /api/signals/?intersection_id=1 — signals per intersection
- GET /api/counts/ — recent vehicle counts
- GET /api/incidents/ — active incidents

## Tech Stack
- Backend: Django 4.2, Django REST Framework
- Frontend: Bootstrap 5, Chart.js, Vanilla JS
- Database: SQLite (dev), PostgreSQL (prod)
- No external APIs — simulation engine built-in
