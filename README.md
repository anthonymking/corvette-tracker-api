# Corvette Tracker API

A FastAPI service that tracks the shipping status of a Corvette using Matson's tracking system.

## Features

- Real-time tracking status updates
- Email notifications for status changes
- Daily status updates at 6am HST
- REST API for status queries

## API Endpoints

- `GET /`: Health check endpoint
- `GET /status`: Get current tracking status

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Run locally:
```bash
python status_api.py
```

3. Access the API:
- Local: http://localhost:8000
- Production: https://corvette-tracker-api.onrender.com

## Environment Variables

- `EMAIL_SENDER`: Gmail address for notifications
- `EMAIL_PASSWORD`: Gmail app password
- `EMAIL_RECIPIENT`: Recipient email address
- `BOOKING_NUMBER`: Matson booking number 