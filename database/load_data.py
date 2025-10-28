# Script to insert data into PostgreSQL
# This will connect CSV files to PostgreSQL database

import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

def load_data_to_postgres():
    """
    Load electricity consumption data from CSV into PostgreSQL database.
    """
    try:
        # 1. Read CSV file from data/ folder
        csv_path = os.path.join('data', 'electricity_raw.csv')
        
        if not os.path.exists(csv_path):
            print(f"❌ Error: CSV file not found at {csv_path}")
            print("Please ensure the file exists in the data/ directory.")
            return False
        
        print(f"📖 Reading CSV file: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"   Loaded {len(df)} rows")
        
        # 2. Filter for Residential sector and years 2022-2024
        print("\n🔍 Filtering data for Residential sector (2022-2024)...")
        df_filtered = df[
            (df['sector'] == 'Residential') &
            (df['year'] >= 2022) &
            (df['year'] <= 2024)
        ].copy()
        print(f"   Filtered to {len(df_filtered)} rows")
        
        if len(df_filtered) == 0:
            print("⚠️  Warning: No data matches the filter criteria")
            return False
        
        # 3. Rename columns to match database schema
        print("\n📝 Renaming columns...")
        column_mapping = {
            'county': 'county',
            'year': 'year',
            'month': 'month',
            'sector': 'sector',
            'consumption_gwh': 'consumption_gwh'
        }
        
        # Check if required columns exist
        required_cols = ['county', 'year', 'month', 'sector', 'consumption_gwh']
        missing_cols = [col for col in required_cols if col not in df_filtered.columns]
        
        if missing_cols:
            print(f"❌ Error: Missing required columns in CSV: {missing_cols}")
            print(f"   Available columns: {df_filtered.columns.tolist()}")
            return False
        
        # Rename columns to match the schema (in case they're different in CSV)
        df_renamed = df_filtered[required_cols].copy()
        
        # Ensure month is integer between 1-12
        if 'month' in df_renamed.columns:
            df_renamed['month'] = pd.to_numeric(df_renamed['month'], errors='coerce')
            df_renamed = df_renamed.dropna(subset=['month'])
            df_renamed = df_renamed[
                (df_renamed['month'] >= 1) & (df_renamed['month'] <= 12)
            ]
        
        # Ensure consumption_gwh is numeric
        if 'consumption_gwh' in df_renamed.columns:
            df_renamed['consumption_gwh'] = pd.to_numeric(df_renamed['consumption_gwh'], errors='coerce')
            df_renamed = df_renamed.dropna(subset=['consumption_gwh'])
        
        print(f"   Final data shape: {df_renamed.shape}")
        print(f"   Sample data:\n{df_renamed.head()}")
        
        # 4. Connect to PostgreSQL using SQLAlchemy
        print("\n🔌 Connecting to PostgreSQL database...")
        db_url = os.getenv('DB_URL')
        
        if not db_url:
            print("❌ Error: DB_URL not found in .env file")
            print("Please create a .env file with DB_URL configuration")
            return False
        
        engine = create_engine(db_url)
        
        # Test the connection
        with engine.connect() as conn:
            print("✅ Successfully connected to database")
        
        # 5. Insert data into power_consumption table
        print("\n💾 Inserting data into power_consumption table...")
        
        # Use if_exists='append' to add data without deleting existing records
        # Use if_exists='replace' to delete and recreate the table
        rows_inserted = df_renamed.to_sql(
            'power_consumption',
            engine,
            if_exists='replace',  # Replace table data
            index=False,
            method='multi'  # Faster insertion for large datasets
        )
        
        print(f"✅ Successfully inserted {rows_inserted} rows into power_consumption table!")
        print("\n📊 Data Summary:")
        print(f"   - Sectors: {df_renamed['sector'].unique()}")
        print(f"   - Years: {sorted(df_renamed['year'].unique())}")
        print(f"   - Counties: {len(df_renamed['county'].unique())}")
        print(f"   - Total consumption: {df_renamed['consumption_gwh'].sum():.2f} GWh")
        
        return True
        
    except pd.errors.EmptyDataError:
        print("❌ Error: CSV file is empty")
        return False
    except pd.errors.ParserError as e:
        print(f"❌ Error: Failed to parse CSV file - {e}")
        return False
    except Exception as e:
        error_type = type(e).__name__
        
        # Check if it's a duplicate key error (IntegrityError)
        if "UniqueViolation" in str(e) or "duplicate key" in str(e).lower():
            print(f"⚠️  Data already exists in the database")
            print(f"   The records from this CSV are already loaded")
            print(f"   To reload, clear the table first or use if_exists='replace' in load_data.py")
            # Don't return False - data exists, which is fine
            return True
        
        print(f"❌ Error occurred: {error_type}")
        print(f"   Details: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 CalPowerCast Data Loader")
    print("=" * 60)
    
    success = load_data_to_postgres()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Data loading completed successfully!")
    else:
        print("❌ Data loading failed. Please check the errors above.")
        sys.exit(1)
    print("=" * 60)

