"""
Train a single unified forecasting model for ALL California counties
Uses XGBoost with county as a categorical feature
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv
import joblib
import json
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

try:
    import xgboost as xgb
except ImportError:
    print("Installing xgboost...")
    os.system("pip install xgboost")
    import xgboost as xgb

load_dotenv()


def create_features(df):
    """Create time-based features from year and month"""
    df = df.copy()
    
    # Create datetime column
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    
    # Time features
    df['year_sin'] = np.sin(2 * np.pi * df['year'] / 4.0)  # Year cycles
    df['year_cos'] = np.cos(2 * np.pi * df['year'] / 4.0)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12.0)  # Seasonal cycles
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12.0)
    
    # Trend
    df['trend'] = df.groupby('county')['date'].transform(
        lambda x: (x - x.min()).dt.days / 365.0
    )
    
    # Lag features (previous month consumption)
    df['lag_1'] = df.groupby('county')['kwh_per_household'].shift(1)
    df['lag_12'] = df.groupby('county')['kwh_per_household'].shift(12)  # Same month last year
    
    # Rolling average
    df['rolling_mean_3'] = df.groupby('county')['kwh_per_household'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    
    return df


def train_unified_model():
    """Train a single model for all counties"""
    
    print("=" * 70)
    print("🏋️  Training Unified Forecasting Model for All Counties")
    print("=" * 70)
    
    # 1. Load data from PostgreSQL
    print("\n📖 Loading data from PostgreSQL...")
    db_url = os.getenv('DB_URL')
    if not db_url:
        raise ValueError("DB_URL not found in .env file")
    
    engine = create_engine(db_url)
    query = """
        SELECT county, year, month, kwh_per_household
        FROM normalized_power
        ORDER BY county, year, month
    """
    df = pd.read_sql(query, engine)
    print(f"   ✅ Loaded {len(df)} records from database")
    print(f"   Counties: {df['county'].nunique()}")
    
    # 2. Create features
    print("\n🔨 Creating features...")
    df = create_features(df)
    df = df.sort_values(['county', 'year', 'month']).reset_index(drop=True)
    
    # 3. Encode county as categorical
    df['county_encoded'] = pd.Categorical(df['county']).codes
    
    # 4. Prepare training data
    # Use data up to 2023 for training, 2024 for validation
    train_df = df[df['year'] <= 2023].copy()
    val_df = df[df['year'] == 2024].copy()
    
    print(f"\n📊 Data split:")
    print(f"   Training: {len(train_df)} records")
    print(f"   Validation: {len(val_df)} records")
    
    # 5. Define features
    feature_cols = [
        'county_encoded',
        'year',
        'month',
        'year_sin', 'year_cos',
        'month_sin', 'month_cos',
        'trend',
        'lag_1', 'lag_12',
        'rolling_mean_3'
    ]
    
    # Remove rows with NaN from lag features
    train_df = train_df.dropna(subset=['lag_1', 'lag_12'])
    val_df = val_df.dropna(subset=['lag_1', 'lag_12'])
    
    X_train = train_df[feature_cols]
    y_train = train_df['kwh_per_household']
    X_val = val_df[feature_cols]
    y_val = val_df['kwh_per_household']
    
    print(f"\n🎯 Training features: {len(feature_cols)}")
    
    # 6. Train XGBoost model
    print("\n🚀 Training XGBoost model...")
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        tree_method='hist',
        enable_categorical=False  # We'll use encoded county
    )
    
    model.fit(X_train, y_train)
    print("   ✅ Model trained")
    
    # 7. Evaluate
    print("\n📈 Evaluating model...")
    y_train_pred = model.predict(X_train)
    y_val_pred = model.predict(X_val)
    
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    train_mae = mean_absolute_error(y_train, y_train_pred)
    train_r2 = r2_score(y_train, y_train_pred)
    
    val_rmse = np.sqrt(mean_squared_error(y_val, y_val_pred))
    val_mae = mean_absolute_error(y_val, y_val_pred)
    val_r2 = r2_score(y_val, y_val_pred)
    
    print(f"\n   Training metrics:")
    print(f"      RMSE: {train_rmse:.2f} kWh/household")
    print(f"      MAE:  {train_mae:.2f} kWh/household")
    print(f"      R²:   {train_r2:.3f}")
    
    print(f"\n   Validation metrics:")
    print(f"      RMSE: {val_rmse:.2f} kWh/household")
    print(f"      MAE:  {val_mae:.2f} kWh/household")
    print(f"      R²:   {val_r2:.3f}")
    
    # 8. Save model and metadata
    print("\n💾 Saving model...")
    os.makedirs('model', exist_ok=True)
    
    # Save model
    model_path = 'model/unified_forecast_model.pkl'
    joblib.dump(model, model_path)
    print(f"   ✅ Model saved: {model_path}")
    
    # Save metadata
    county_mapping = dict(zip(df['county_encoded'].unique(), df['county'].unique()))
    # Convert numpy types to Python native types for JSON serialization
    county_mapping = {int(k): str(v) for k, v in county_mapping.items()}
    
    metadata = {
        'model_type': 'xgboost_unified',
        'counties': sorted(df['county'].unique().tolist()),
        'total_counties': df['county'].nunique(),
        'features': feature_cols,
        'training_records': len(train_df),
        'validation_records': len(val_df),
        'training_rmse': float(train_rmse),
        'training_mae': float(train_mae),
        'training_r2': float(train_r2),
        'validation_rmse': float(val_rmse),
        'validation_mae': float(val_mae),
        'validation_r2': float(val_r2),
        'county_mapping': county_mapping,
        'train_date': datetime.now().isoformat()
    }
    
    metadata_path = 'model/unified_model_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"   ✅ Metadata saved: {metadata_path}")
    
    print("\n" + "=" * 70)
    print("✅ Unified model training completed successfully!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   Counties: {df['county'].nunique()}")
    print(f"   Validation RMSE: {val_rmse:.2f} kWh/household")
    print(f"   Model can predict for ANY county in the database")
    
    return model, metadata


if __name__ == '__main__':
    train_unified_model()

