"""
CalPowerCast API for Hugging Face Spaces
Simplified version without database dependencies
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from forecast import get_forecast, list_available_counties

app = FastAPI(
    title="CalPowerCast API",
    description="Machine learning forecasting API for California household electricity usage",
    version="1.0.0"
)

# Allow all origins for Hugging Face deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/health")
async def health():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy", "service": "CalPowerCast"}

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

