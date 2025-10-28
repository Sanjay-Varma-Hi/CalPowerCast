# FastAPI application for CalPowerCast
# This file will hold the FastAPI app

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from data_loader import test_database_connection
from forecast import get_forecast, list_available_counties

# Create FastAPI app instance
app = FastAPI(
    title="CalPowerCast API",
    description="Machine learning forecasting API for California household electricity usage",
    version="1.0.0"
)

# Add CORS middleware to allow requests from localhost:3000 (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
async def root():
    """
    Root endpoint that returns a simple health check message.
    """
    return {
        "message": "CalPowerCast ML API is running",
        "description": "Machine learning forecasting API for California household electricity usage",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
async def health():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy", "service": "CalPowerCast"}

# Database health check endpoint
@app.get("/health/db")
async def health_db():
    """
    Database health check endpoint.
    Tests database connectivity and returns connection status.
    """
    success, message, count = test_database_connection()
    
    if success:
        return {
            "status": "healthy",
            "database": "connected",
            "record_count": count,
            "message": message
        }
    else:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "message": message
        }


@app.get("/forecast")
async def forecast(county: str = Query(..., description="California county name"), 
                   periods: int = Query(12, description="Number of months to forecast")):
    """
    Generate electricity usage forecast for a specific California county.
    
    Args:
        county: Name of the county (e.g., "Santa Clara", "Los Angeles")
        periods: Number of months to forecast (default: 12, max: 36)
    
    Returns:
        JSON object containing forecast predictions with dates and kWh per household estimates
    
    Example:
        GET /forecast?county=Santa%20Clara&periods=12
    """
    # Validate periods
    if periods < 1 or periods > 36:
        raise HTTPException(status_code=400, detail="Periods must be between 1 and 36")
    
    try:
        result = get_forecast(county, periods)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")


@app.get("/counties")
async def counties():
    """
    List all counties with trained models available for forecasting.
    
    Returns:
        JSON object containing list of available counties
    """
    available_counties = list_available_counties()
    return {
        "total_counties": len(available_counties),
        "counties": available_counties
    }


if __name__ == "__main__":
    # Run the app with auto-reload
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."]
    )

