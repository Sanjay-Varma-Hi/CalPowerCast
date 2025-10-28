#!/usr/bin/env python
"""
Generate realistic sample data for all 58 California counties (2020-2024)
Based on actual California demographics and energy patterns
"""

import pandas as pd
import random
import os

# All 58 California Counties with approximate population/economic weights
CALIFORNIA_COUNTIES = [
    ('Los Angeles', 10000000, 3800000),      # Largest population
    ('San Diego', 3300000, 1200000),
    ('Orange', 3200000, 1100000),
    ('Riverside', 2450000, 800000),
    ('San Bernardino', 2180000, 700000),
    ('Santa Clara', 1900000, 630000),
    ('Alameda', 1680000, 560000),
    ('Sacramento', 1570000, 560000),
    ('Contra Costa', 1160000, 420000),
    ('Fresno', 1010000, 340000),
    ('Ventura', 846000, 280000),
    ('San Francisco', 873000, 360000),
    ('Kern', 909000, 290000),
    ('San Mateo', 764000, 280000),
    ('Sonoma', 495000, 180000),
    ('Monterey', 435000, 145000),
    ('Santa Barbara', 446000, 165000),
    ('Placer', 412000, 145000),
    ('San Joaquin', 779000, 250000),
    ('Solano', 447000, 155000),
    ('Stanislaus', 551000, 180000),
    ('Tulare', 473000, 150000),
    ('Santa Cruz', 274000, 105000),
    ('Marin', 258000, 102000),
    ('Butte', 211000, 83000),
    ('El Dorado', 192000, 70000),
    ('Imperial', 179000, 57000),
    ('Shasta', 181000, 70000),
    ('Yolo', 216000, 84000),
    ('Merced', 281000, 90000),
    ('San Luis Obispo', 282000, 110000),
    ('Humboldt', 136000, 51000),
    ('Napa', 138000, 55000),
    ('Kings', 152000, 50000),
    ('Mendocino', 88100, 33000),
    ('Yuba', 81400, 29000),
    ('Madera', 157000, 52000),
    ('Tehama', 65600, 24000),
    ('Tuolumne', 54400, 21000),
    ('San Benito', 64500, 24000),
    ('Nevada', 102000, 40000),
    ('Tulare', 473000, 150000),
    ('Calaveras', 45900, 17000),
    ('Amador', 41200, 15000),
    ('Sierra', 3100, 1200),
    ('Alpine', 1115, 450),
    ('Inyo', 18900, 7400),
    ('Mariposa', 17400, 7000),
    ('Mono', 13600, 5300),
    ('Glenn', 28700, 11000),
    ('Colusa', 21500, 8300),
    ('Sutter', 98600, 34000),
    ('Modoc', 8800, 3300),
    ('Lassen', 30900, 12000),
    ('Lake', 68100, 26000),
    ('Del Norte', 27000, 10000),
    ('Siskiyou', 44000, 17000),
    ('Plumas', 19400, 7600),
]


def generate_realistic_data():
    print("=" * 60)
    print("🏗️  Generating Realistic Sample Data")
    print("   58 California Counties, 2020-2024")
    print("=" * 60)
    
    # Set seed for reproducibility
    random.seed(42)
    
    # Generate Household Data
    print("\n📊 Generating household data...")
    households_data = []
    
    for county_name, population, households in CALIFORNIA_COUNTIES:
        for year in range(2020, 2025):
            # Add realistic growth variation (1-3% per year)
            year_offset = year - 2020
            growth_factor = 1.0 + (year_offset * 0.015)  # 1.5% average growth
            
            # Add random variation per year
            variation = random.uniform(-0.02, 0.02)
            
            # Calculate households for this year
            year_households = int(households * growth_factor * (1 + variation))
            
            households_data.append({
                'county': county_name,
                'year': year,
                'households': year_households
            })
    
    households_df = pd.DataFrame(households_data)
    households_df.to_csv('data/households.csv', index=False)
    print(f"   ✅ Created households.csv: {len(households_df)} records")
    print(f"   Counties: {len(CALIFORNIA_COUNTIES)}")
    print(f"   Years: 2020-2024")
    
    # Generate Electricity Consumption Data
    print("\n⚡ Generating electricity consumption data...")
    electricity_data = []
    
    for county_name, population, households in CALIFORNIA_COUNTIES:
        for year in [2022, 2023, 2024]:  # Only 2022-2024 for electricity
            for month in range(1, 13):
                # Get household count for this year
                county_households_data = households_df[
                    (households_df['county'] == county_name) & 
                    (households_df['year'] == year)
                ]
                
                if len(county_households_data) > 0:
                    num_households = county_households_data.iloc[0]['households']
                    
                    # Base consumption per household (kWh per month)
                    # Typical CA household uses 500-900 kWh/month (varies by region)
                    base_monthly_kwh = random.uniform(550, 850)
                    
                    # Adjust for county size/wealth (urban vs rural)
                    if population > 3000000:  # Major metro areas
                        base_monthly_kwh *= 0.9  # Slightly lower (efficiency)
                    elif population < 50000:  # Rural areas
                        base_monthly_kwh *= 1.2  # Higher (heating/cooling less efficient)
                    
                    # Seasonal variation (real CA electricity patterns)
                    seasonal_multiplier = 1.0
                    if month in [7, 8]:  # Peak summer (AC)
                        seasonal_multiplier = 1.35
                    elif month in [6, 9]:  # Early/late summer
                        seasonal_multiplier = 1.15
                    elif month in [12, 1]:  # Winter heating
                        seasonal_multiplier = 1.20
                    elif month in [2, 3]:  # Late winter
                        seasonal_multiplier = 1.10
                    elif month in [4, 5, 10, 11]:  # Moderate months
                        seasonal_multiplier = 0.95
                    
                    # Calculate monthly consumption in kWh
                    monthly_kwh = base_monthly_kwh * seasonal_multiplier
                    
                    # Add random variation
                    monthly_kwh *= random.uniform(0.95, 1.05)
                    
                    # Convert kWh to GWh
                    monthly_gwh = (monthly_kwh * num_households) / 1_000_000
                    
                    electricity_data.append({
                        'county': county_name,
                        'year': year,
                        'month': month,
                        'sector': 'Residential',
                        'consumption_gwh': round(monthly_gwh, 3)
                    })
    
    electricity_df = pd.DataFrame(electricity_data)
    electricity_df.to_csv('data/electricity_raw.csv', index=False)
    print(f"   ✅ Created electricity_raw.csv: {len(electricity_df)} records")
    print(f"   Counties: {len(CALIFORNIA_COUNTIES)}")
    print(f"   Years: 2022-2024")
    print(f"   Total months: {len(electricity_df) // len(CALIFORNIA_COUNTIES)} months")
    
    # Print summary statistics
    print("\n📈 Data Summary:")
    print(f"   Total household records: {len(households_df)}")
    print(f"   Total electricity records: {len(electricity_df)}")
    print(f"   Total households (2024): {households_df[households_df['year']==2024]['households'].sum():,}")
    print(f"   Avg electricity per record: {electricity_df['consumption_gwh'].mean():.3f} GWh")
    
    print("\n" + "=" * 60)
    print("✅ Sample data generation complete!")
    print("=" * 60)
    print("\n⚠️  Remember: This is SAMPLE data based on realistic patterns")
    print("   You will need to replace with real data from government sources")
    print("\n📁 Files created:")
    print("   - data/households.csv")
    print("   - data/electricity_raw.csv")
    print("\n📋 Next step: python backend/normalize_data.py")


if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    generate_realistic_data()

