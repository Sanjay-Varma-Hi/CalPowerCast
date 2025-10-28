"""
Unified forecast module - uses single model for all counties
"""

import os
import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime, timedelta


def create_features(df):
    """Create time-based features from year and month"""
    df = df.copy()
    
    # Create datetime column
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    
    # Time features
    df['year_sin'] = np.sin(2 * np.pi * df['year'] / 4.0)
    df['year_cos'] = np.cos(2 * np.pi * df['year'] / 4.0)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12.0)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12.0)
    
    # Trend (relative to first date in dataset)
    min_date = df['date'].min()
    df['trend'] = (df['date'] - min_date).dt.days / 365.0
    
    # For future predictions, we'll need to handle lags differently
    # We'll set them to the last known values or use a forward-fill approach
    df['lag_1'] = df['kwh_per_household'].shift(1)
    df['lag_12'] = df['kwh_per_household'].shift(12)
    df['rolling_mean_3'] = df['kwh_per_household'].rolling(window=3, min_periods=1).mean()
    
    return df


def get_forecast(county: str, periods: int = 12):
    """
    Get forecast using the unified model for any county.
    
    Args:
        county: Name of the California county
        periods: Number of months to forecast
    
    Returns:
        dict: Forecast predictions
    """
    # Load model and metadata
    # Path relative to backend directory
    model_path = os.path.join(os.path.dirname(__file__), "..", "model", "unified_forecast_model.pkl")
    metadata_path = os.path.join(os.path.dirname(__file__), "..", "model", "unified_model_metadata.json")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Please train the model first.")
    
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata not found at {metadata_path}.")
    
    # Load model and metadata
    model = joblib.load(model_path)
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Check if county exists in training data
    if county not in metadata['counties']:
        raise ValueError(
            f"County '{county}' not found in model. "
            f"Available counties: {', '.join(metadata['counties'])}"
        )
    
    # Get county encoding
    county_mapping = {v: k for k, v in metadata['county_mapping'].items()}
    county_encoded = county_mapping[county]
    
    # Load historical data for this county to get context
    # For simplicity, we'll use the model to generate forecasts based on time features only
    # In production, you'd load recent actuals to compute lags
    
    # Generate future dates
    start_date = datetime(2024, 12, 1)  # Start from last month
    future_dates = [start_date + timedelta(days=31*i) for i in range(1, periods+1)]
    
    # Create future dataframe
    future_data = []
    for i, date in enumerate(future_dates):
        year = date.year
        month = date.month
        
        # Create features for this future point
        features = {
            'county_encoded': county_encoded,
            'year': year,
            'month': month,
            'year_sin': np.sin(2 * np.pi * year / 4.0),
            'year_cos': np.cos(2 * np.pi * year / 4.0),
            'month_sin': np.sin(2 * np.pi * month / 12.0),
            'month_cos': np.cos(2 * np.pi * month / 12.0),
            'trend': 3.5 + i / 12.0,  # Estimated trend
            'lag_1': None,  # Will fill with prediction
            'lag_12': None,  # Will fill with prediction
            'rolling_mean_3': None  # Will fill with prediction
        }
        future_data.append(features)
    
    # Simple forward-fill approach for lags (use previous predictions)
    # This is a simplification - in production you'd use actual historical data
    for i in range(len(future_data)):
        # Use a simple seasonal average as lag estimates
        avg_kwh = 800  # Reasonable estimate
        future_data[i]['lag_1'] = float(avg_kwh)
        future_data[i]['lag_12'] = float(avg_kwh)
        future_data[i]['rolling_mean_3'] = float(avg_kwh)
    
    # Convert to DataFrame with proper dtypes
    feature_cols = metadata['features']
    future_df = pd.DataFrame(future_data)[feature_cols]
    
    # Ensure proper data types
    future_df['county_encoded'] = future_df['county_encoded'].astype(int)
    for col in ['year', 'month']:
        future_df[col] = future_df[col].astype(int)
    
    # Generate predictions
    predictions = model.predict(future_df)
    
    # Format results
    forecast = []
    for i, (date, pred) in enumerate(zip(future_dates, predictions)):
        # Calculate confidence interval (simplified)
        std_error = np.std(predictions) * 0.1  # Rough estimate
        lower_bound = pred - 1.96 * std_error
        upper_bound = pred + 1.96 * std_error
        
        forecast.append({
            'date': date.strftime('%Y-%m-%d'),
            'predicted_kwh': round(float(pred), 2),
            'lower_bound': round(max(0, float(lower_bound)), 2),
            'upper_bound': round(float(upper_bound), 2)
        })
    
    return {
        'county': county,
        'periods': periods,
        'model_type': 'unified_xgboost',
        'forecast': forecast
    }


def list_available_counties():
    """List all counties available in the unified model"""
    metadata_path = os.path.join(os.path.dirname(__file__), "..", "model", "unified_model_metadata.json")
    
    if not os.path.exists(metadata_path):
        return []
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    return sorted(metadata['counties'])


if __name__ == "__main__":
    # Test the function
    print("Testing unified forecast...")
    counties = list_available_counties()
    print(f"Available counties: {len(counties)}")
    print(counties[:5])
    
    if counties:
        result = get_forecast_unified(counties[0], periods=6)
        print(f"\nForecast for {result['county']}:")
        for pred in result['forecast'][:3]:
            print(f"  {pred['date']}: {pred['predicted_kwh']} kWh/household")

