"""
Load household data into PostgreSQL
"""

import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def load_households_to_db():
    """Load household data into PostgreSQL"""
    print("=" * 60)
    print("🏠 Loading Household Data to PostgreSQL")
    print("=" * 60)
    
    # Read CSV
    csv_path = os.path.join('data', 'households.csv')
    print(f"📖 Reading: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"   Loaded {len(df)} records")
    
    # Connect to database
    db_url = os.getenv('DB_URL')
    engine = create_engine(db_url)
    
    print("\n💾 Inserting into PostgreSQL...")
    df.to_sql('households', engine, if_exists='replace', index=False)
    
    print(f"✅ Successfully inserted {len(df)} records")
    print("=" * 60)

if __name__ == '__main__':
    load_households_to_db()

