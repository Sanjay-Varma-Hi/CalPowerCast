# CalPowerCast

Machine learning forecasting API for California household electricity usage prediction.

## Quick Start

### Test the API Locally

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs

### API Endpoints

- `GET /` - Health check
- `GET /forecast?county=Santa%20Clara&periods=12` - Get forecast
- `GET /counties` - List available counties

### Available Counties

- Los Angeles
- Orange
- Sacramento
- San Diego
- Santa Clara

## Hugging Face Deployment

This Space is configured to run on Hugging Face with Docker SDK.

### Files Included

- `app.py` - FastAPI application
- `forecast.py` - ML forecasting logic
- `model/` - Trained Prophet models
- `Dockerfile` - Container configuration
