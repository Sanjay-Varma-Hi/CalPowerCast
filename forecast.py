"""
Forecast module for CalPowerCast API
Provides functions to load trained Prophet models and generate predictions
"""

import os
import pandas as pd
import joblib
from prophet import Prophet


def get_forecast(county: str, periods: int = 12) -> dict:
    """
    Load a trained Prophet model and generate forecasts for the specified county.
    
    Args:
        county: Name of the California county (e.g., "Santa Clara", "Los Angeles")
        periods: Number of months to forecast into the future (default: 12)
    
    Returns:
        dict: Dictionary containing forecast data with keys:
            - 'county': The county name
            - 'forecast': List of forecasted values
            - 'dates': List of future dates
            - 'periods': Number of forecasted periods
    
    Raises:
        FileNotFoundError: If the model file doesn't exist for the given county
        Exception: If there's an error loading or using the model
    """
    # Normalize county name to match model file naming convention
    # Convert spaces to underscores (e.g., "Santa Clara" -> "Santa_Clara")
    county_normalized = county.replace(" ", "_")
    
    # Construct model file path
    model_dir = os.path.join(os.path.dirname(__file__), "..", "model")
    model_filename = f"{county_normalized}_prophet_model.pkl"
    model_path = os.path.join(model_dir, model_filename)
    
    # Check if model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found for county '{county}'. "
            f"Expected file: {model_path}. "
            f"Available models: {', '.join([f.replace('_prophet_model.pkl', '').replace('_', ' ') for f in os.listdir(model_dir) if f.endswith('_prophet_model.pkl')])}"
        )
    
    # Load the trained model
    try:
        model = joblib.load(model_path)
    except Exception as e:
        raise Exception(f"Error loading model for {county}: {str(e)}")
    
    # Generate future dataframe
    try:
        future = model.make_future_dataframe(periods=periods, freq='M')
    except Exception as e:
        raise Exception(f"Error creating future dataframe: {str(e)}")
    
    # Generate forecast
    try:
        forecast = model.predict(future)
    except Exception as e:
        raise Exception(f"Error generating forecast: {str(e)}")
    
    # Extract only the future predictions (last 'periods' rows)
    forecast_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
    
    # Convert to dictionary format for JSON response
    return {
        'county': county,
        'periods': periods,
        'forecast': [
            {
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted_kwh': round(float(row['yhat']), 2),
                'lower_bound': round(float(row['yhat_lower']), 2),
                'upper_bound': round(float(row['yhat_upper']), 2)
            }
            for _, row in forecast_df.iterrows()
        ]
    }


def list_available_counties() -> list:
    """
    Get a list of all counties that have trained models available.
    
    Returns:
        list: List of county names with trained models
    """
    model_dir = os.path.join(os.path.dirname(__file__), "..", "model")
    
    if not os.path.exists(model_dir):
        return []
    
    # Extract county names from model files
    county_names = []
    for filename in os.listdir(model_dir):
        if filename.endswith('_prophet_model.pkl'):
            county_name = filename.replace('_prophet_model.pkl', '').replace('_', ' ')
            county_names.append(county_name)
    
    return sorted(county_names)


if __name__ == "__main__":
    # Test the function
    print("Testing forecast function...")
    
    # List available counties
    available = list_available_counties()
    print(f"\nAvailable counties: {', '.join(available)}")
    
    # Test forecast for Santa Clara
    if available:
        test_county = available[0]
        print(f"\nTesting forecast for: {test_county}")
        result = get_forecast(test_county, periods=6)
        print(f"\nForecast for {result['county']}:")
        for pred in result['forecast'][:3]:  # Show first 3 predictions
            print(f"  {pred['date']}: {pred['predicted_kwh']} kWh/household")
        print(f"... and {len(result['forecast']) - 3} more months")

