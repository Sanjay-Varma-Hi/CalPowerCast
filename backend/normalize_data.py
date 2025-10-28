"""
Normalize electricity consumption data per household by county, year, and month.
"""

import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()


def normalize_consumption():
    """
    Normalize electricity consumption per household by county, year, and month.
    
    Loads electricity and household data, merges them, calculates kWh per household,
    and saves to both CSV and PostgreSQL.
    
    Returns:
        pandas.DataFrame: Normalized consumption data sorted by county, year, month
    """
    try:
        print("=" * 60)
        print("🔄 CalPowerCast Data Normalization")
        print("=" * 60)
        
        # 1. Load data from PostgreSQL database
        print("\n📖 Loading data from PostgreSQL database...")
        
        db_url = os.getenv('DB_URL')
        if not db_url:
            print("❌ Error: DB_URL not found in .env file")
            return None
        
        engine = create_engine(db_url)
        print("   ✅ Connected to database")
        
        # Load electricity data from power_consumption table
        print("   Loading electricity data from power_consumption table...")
        electricity_df = pd.read_sql("SELECT * FROM power_consumption", engine)
        print(f"   Electricity data: {len(electricity_df)} rows")
        
        # Load households data from households table
        print("   Loading households data from households table...")
        households_df = pd.read_sql("SELECT * FROM households", engine)
        print(f"   Households data: {len(households_df)} rows")
        
        # 2. Filter electricity data
        print("\n🔍 Filtering electricity data...")
        print("   Filtering for: Sector=Residential, Years=2022-2024")
        
        # Filter for Residential sector and years 2022-2024
        filtered_df = electricity_df[
            (electricity_df['sector'] == 'Residential') &
            (electricity_df['year'] >= 2022) &
            (electricity_df['year'] <= 2024)
        ].copy()
        
        print(f"   Filtered to: {len(filtered_df)} rows")
        
        if len(filtered_df) == 0:
            print("❌ Error: No data matches the filter criteria")
            return None
        
        # 3. Check required columns in electricity data
        required_cols = ['county', 'year', 'month', 'consumption_gwh']
        missing_cols = [col for col in required_cols if col not in filtered_df.columns]
        
        if missing_cols:
            print(f"❌ Error: Missing required columns in electricity data: {missing_cols}")
            print(f"   Available columns: {filtered_df.columns.tolist()}")
            return None
        
        # 4. Check required columns in households data
        household_cols = ['county', 'year', 'households']
        missing_cols = [col for col in household_cols if col not in households_df.columns]
        
        if missing_cols:
            print(f"❌ Error: Missing required columns in households data: {missing_cols}")
            print(f"   Available columns: {households_df.columns.tolist()}")
            return None
        
        # 5. Merge data on county and year
        print("\n🔗 Merging electricity and household data...")
        
        # Select only needed columns for merge
        electricity_merge = filtered_df[['county', 'year', 'month', 'consumption_gwh']].copy()
        households_merge = households_df[['county', 'year', 'households']].copy()
        
        # Perform merge
        merged_df = electricity_merge.merge(
            households_merge,
            on=['county', 'year'],
            how='inner'  # Only keep records that exist in both
        )
        
        print(f"   After merge: {len(merged_df)} rows")
        
        if len(merged_df) == 0:
            print("❌ Error: No matching records after merge")
            print("   Check that county and year values match between datasets")
            return None
        
        # 6. Check for mismatches
        unmatched = len(filtered_df) - len(merged_df)
        if unmatched > 0:
            print(f"⚠️  Warning: {unmatched} electricity records unmatched (no household data)")
        
        # 7. Check for NaN values
        print("\n🔍 Checking data quality...")
        nan_counts = merged_df.isnull().sum()
        if nan_counts.sum() > 0:
            print(f"⚠️  Warning: Found NaN values:")
            for col, count in nan_counts[nan_counts > 0].items():
                print(f"   {col}: {count}")
            
            # Drop rows with NaN values
            rows_before = len(merged_df)
            merged_df = merged_df.dropna()
            rows_after = len(merged_df)
            print(f"   Removed {rows_before - rows_after} rows with NaN values")
        
        # 8. Calculate kWh per household
        print("\n🧮 Calculating kWh per household...")
        
        # Convert GWh to kWh and divide by households
        merged_df['kwh_per_household'] = (
            merged_df['consumption_gwh'] * 1_000_000
        ) / merged_df['households']
        
        # Select final columns
        result_df = merged_df[['county', 'year', 'month', 'kwh_per_household']].copy()
        
        # 9. Print statistics
        print("\n📊 Data Statistics:")
        print(f"   Total records: {len(result_df)}")
        print(f"   Counties: {len(result_df['county'].unique())}")
        print(f"   Years: {sorted(result_df['year'].unique())}")
        print(f"   Min kWh/household: {result_df['kwh_per_household'].min():.2f}")
        print(f"   Max kWh/household: {result_df['kwh_per_household'].max():.2f}")
        print(f"   Mean kWh/household: {result_df['kwh_per_household'].mean():.2f}")
        
        # 10. Sort by county, year, month
        result_df = result_df.sort_values(['county', 'year', 'month']).reset_index(drop=True)
        print(f"   Data sorted by county, year, month")
        
        # 11. Save to PostgreSQL (main storage)
        print("\n💾 Saving to PostgreSQL...")
        
        # Get database connection
        db_url = os.getenv('DB_URL')
        if not db_url:
            print("❌ Error: DB_URL not found in .env file")
            return result_df
        
        # Create engine
        engine = create_engine(db_url)
        
        # Connect and insert data
        print("   Connecting to database...")
        with engine.connect() as conn:
            print("   ✅ Connected")
        
        print("   Inserting data into normalized_power table...")
        result_df.to_sql(
            'normalized_power',
            engine,
            if_exists='replace',  # Replace table if it exists
            index=False
        )
        print("   ✅ Data inserted successfully")
        
        # Print summary
        print("\n" + "=" * 60)
        print("✅ Normalization completed successfully!")
        print("=" * 60)
        print(f"\n📁 Output:")
        print(f"   PostgreSQL: normalized_power table ({len(result_df)} rows)")
        print(f"   ✅ All data now stored in PostgreSQL database")
        
        return result_df
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return None
    except pd.errors.EmptyDataError:
        print("❌ Error: CSV file is empty")
        return None
    except pd.errors.ParserError as e:
        print(f"❌ Error: Failed to parse CSV file - {e}")
        return None
    except Exception as e:
        print(f"❌ Error occurred: {type(e).__name__}")
        print(f"   Details: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    result = normalize_consumption()
    
    if result is not None:
        print("\n" + "=" * 60)
        print("📋 Sample data:")
        print(result.head(10))
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n❌ Normalization failed")
        sys.exit(1)

