"""
Train Prophet Forecasting Model for CalPowerCast
Trains time series models to predict electricity consumption per county
"""

import pandas as pd
from prophet import Prophet
import joblib
import os
import json
from typing import Dict, Tuple
from datetime import datetime
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


def train_forecasting_model(county_name: str = "Santa Clara") -> Tuple[Prophet, pd.DataFrame]:
    """
    Train a Prophet time series forecasting model for electricity consumption.
    
    Args:
        county_name: Name of the county to train model for
        
    Returns:
        tuple: (trained_model, forecast_dataframe)
    """
    print("=" * 70)
    print(f"🚂 Training Prophet Model for: {county_name}")
    print("=" * 70)
    
    # 1. Load data from PostgreSQL database
    print("\n📖 Loading normalized consumption data from PostgreSQL...")
    
    db_url = os.getenv('DB_URL')
    if not db_url:
        raise ValueError("DB_URL not found in .env file")
    
    engine = create_engine(db_url)
    
    # Query normalized_power table
    query = f"""
        SELECT county, year, month, kwh_per_household
        FROM normalized_power
        WHERE county = '{county_name}'
        ORDER BY year, month
    """
    
    print(f"   Querying database for {county_name}...")
    df = pd.read_sql(query, engine)
    
    if len(df) == 0:
        # Get list of available counties
        available_query = "SELECT DISTINCT county FROM normalized_power LIMIT 10"
        available_df = pd.read_sql(available_query, engine)
        available_counties = available_df['county'].tolist()
        
        raise ValueError(
            f"County '{county_name}' not found in database.\n"
            f"Available counties: {', '.join(available_counties)}..."
        )
    
    print(f"   Loaded {len(df)} records from database")
    
    # Use df as county_data
    county_data = df.copy()
    
    print(f"   Found {len(county_data)} records for {county_name}")
    
    # 3. Convert year and month to datetime format (ds column)
    print("\n📅 Converting year/month to datetime...")
    county_data['ds'] = pd.to_datetime(
        county_data[['year', 'month']].assign(day=1)
    )
    
    # 4. Rename kwh_per_household to y (Prophet requirement)
    county_data['y'] = county_data['kwh_per_household']
    
    # 5. Select only required columns for Prophet
    prophet_data = county_data[['ds', 'y']].copy()
    
    # 6. Drop any rows with missing values
    rows_before = len(prophet_data)
    prophet_data = prophet_data.dropna()
    rows_after = len(prophet_data)
    
    if rows_before != rows_after:
        print(f"   ⚠️  Removed {rows_before - rows_after} rows with missing values")
    
    print(f"   Prepared {len(prophet_data)} records for training")
    print(f"   Date range: {prophet_data['ds'].min()} to {prophet_data['ds'].max()}")
    
    # 7. Sort by date (important for time series)
    prophet_data = prophet_data.sort_values('ds').reset_index(drop=True)
    
    # 8. Instantiate and train Prophet model
    print("\n🤖 Training Prophet model...")
    print("   Model parameters: default Prophet settings with yearly seasonality")
    
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,  # Monthly data, no weekly pattern
        daily_seasonality=False,
        seasonality_mode='multiplicative'  # Multiplicative handles growth
    )
    
    # Add custom seasonality for monthly patterns
    model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
    
    # Train the model
    model.fit(prophet_data)
    print("   ✅ Model training complete")
    
    # 9. Make predictions for next 12 months
    print("\n🔮 Generating forecast for next 12 months...")
    future = model.make_future_dataframe(periods=12, freq='M')
    forecast = model.predict(future)
    
    print(f"   Created forecast with {len(forecast)} data points")
    print(f"   Predictions extend to: {forecast['ds'].max()}")
    
    # 10. Save the trained model
    print("\n💾 Saving trained model...")
    model_dir = os.path.join('model')
    os.makedirs(model_dir, exist_ok=True)
    
    # Sanitize county name for filename
    county_filename = county_name.replace(' ', '_').replace(',', '')
    model_path = os.path.join(model_dir, f'{county_filename}_prophet_model.pkl')
    
    joblib.dump(model, model_path)
    print(f"   ✅ Model saved to: {model_path}")
    
    # 11. Save forecast to CSV
    forecast_output_path = f'forecast_{county_filename}.csv'
    
    # Select relevant columns for output
    forecast_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    forecast_df.columns = ['date', 'predicted_kwh', 'lower_bound', 'upper_bound']
    
    forecast_df.to_csv(forecast_output_path, index=False)
    print(f"   ✅ Forecast saved to: {forecast_output_path}")
    
    # 12. Print key forecast statistics
    print("\n📊 Forecast Statistics:")
    print("-" * 70)
    
    # Last 6 predicted months (future predictions)
    last_six_months = forecast.tail(6)
    print("\n🔮 Last 6 Months Predictions:")
    print(last_six_months[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_string(index=False))
    
    # Calculate and print RMSE if we have actual data for comparison
    if len(prophet_data) > 0:
        # Get predictions for historical data (training period)
        historical_predictions = forecast[forecast['ds'] <= prophet_data['ds'].max()]
        
        if len(historical_predictions) == len(prophet_data):
            # Calculate RMSE and MAE
            rmse = np.sqrt(np.mean((prophet_data['y'] - historical_predictions['yhat'])**2))
            mae = np.mean(np.abs(prophet_data['y'] - historical_predictions['yhat']))
            
            print(f"\n📈 Model Performance Metrics:")
            print(f"   RMSE: {rmse:.2f} kWh/household")
            print(f"   MAE:  {mae:.2f} kWh/household")
            
            # Print summary statistics
            print(f"\n📊 Data Summary for {county_name}:")
            print(f"   Training period: {len(prophet_data)} months")
            print(f"   Actual avg consumption: {prophet_data['y'].mean():.2f} kWh/household")
            print(f"   Actual consumption range: {prophet_data['y'].min():.1f} - {prophet_data['y'].max():.1f} kWh/household")
    
    print("\n" + "=" * 70)
    print(f"✅ Training complete for {county_name}!")
    print("=" * 70)
    
    return model, forecast


def evaluate_model(model: Prophet, df: pd.DataFrame, forecast: pd.DataFrame, 
                   county_name: str) -> Dict:
    """
    Evaluate model performance with metrics.
    
    Args:
        model: Trained Prophet model
        df: Training dataframe with actual values
        forecast: Forecast dataframe from Prophet
        county_name: County name for identification
        
    Returns:
        dict: Metrics dictionary
    """
    print("\n📊 Evaluating Model Performance...")
    
    # Get predictions for training period (historical data)
    historical_predictions = forecast[forecast['ds'] <= df['ds'].max()].copy()
    
    # Ensure same length
    min_len = min(len(df), len(historical_predictions))
    
    # Calculate metrics
    actual = df['y'].values[:min_len]
    predicted = historical_predictions['yhat'].values[:min_len]
    
    rmse = np.sqrt(np.mean((actual - predicted)**2))
    mae = np.mean(np.abs(actual - predicted))
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    
    # R-squared
    ss_res = np.sum((actual - predicted)**2)
    ss_tot = np.sum((actual - np.mean(actual))**2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    metrics = {
        'county': county_name,
        'rmse': round(rmse, 4),
        'mae': round(mae, 4),
        'mape': round(mape, 2),
        'r2_score': round(r2, 4),
        'training_samples': len(df),
        'evaluation_date': datetime.now().isoformat()
    }
    
    print("   Model Metrics:")
    print(f"   - RMSE: {metrics['rmse']:.2f} kWh/household")
    print(f"   - MAE: {metrics['mae']:.2f} kWh/household")
    print(f"   - MAPE: {metrics['mape']:.2f}%")
    print(f"   - R² Score: {metrics['r2_score']:.4f}")
    
    # Save metrics to JSON
    metrics_path = f'model/{county_name.replace(" ", "_")}_metrics.json'
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"   ✅ Metrics saved to: {metrics_path}")
    
    return metrics


def main():
    """Main function to train model"""
    import sys
    
    # Default county to train
    county = "Santa Clara"
    
    # Allow county name as command line argument
    if len(sys.argv) > 1:
        county = " ".join(sys.argv[1:])
    
    try:
        # Train the model
        model, forecast = train_forecasting_model(county_name=county)
        
        # Load the actual data for evaluation from database
        db_url = os.getenv('DB_URL')
        engine = create_engine(db_url)
        
        query = f"""
            SELECT county, year, month, kwh_per_household
            FROM normalized_power
            WHERE county = '{county}'
            ORDER BY year, month
        """
        
        df = pd.read_sql(query, engine)
        county_data = df.copy()
        county_data['ds'] = pd.to_datetime(
            county_data[['year', 'month']].assign(day=1)
        )
        county_data['y'] = county_data['kwh_per_household']
        county_data = county_data.sort_values('ds').reset_index(drop=True)
        
        # Evaluate the model
        metrics = evaluate_model(model, county_data, forecast, county)
        
        print("\n✅ All tasks completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

