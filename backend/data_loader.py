# Database utilities for CalPowerCast
# This file contains database connection and testing functions

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_database_connection():
    """
    Test database connectivity by loading the connection URL from .env,
    connecting with SQLAlchemy, and running a simple query.
    
    Returns:
        tuple: (success: bool, message: str, count: int or None)
    """
    try:
        # 1. Load DB connection URL from .env
        print("📋 Loading database connection URL from .env...")
        db_url = os.getenv('DB_URL')
        
        if not db_url:
            error_msg = "❌ Error: DB_URL not found in .env file"
            print(error_msg)
            print("   Please ensure .env file exists with DB_URL configuration")
            return False, error_msg, None
        
        print(f"   Found DB_URL configuration")
        
        # 2. Connect using SQLAlchemy
        print("\n🔌 Connecting to PostgreSQL database...")
        engine = create_engine(db_url)
        
        # Test the connection
        with engine.connect() as conn:
            print("✅ Successfully connected to database")
            
            # 3. Run a simple query: SELECT COUNT(*) FROM power_consumption
            print("\n📊 Running test query: SELECT COUNT(*) FROM power_consumption...")
            result = conn.execute(text("SELECT COUNT(*) as count FROM power_consumption"))
            count = result.fetchone()[0]
            
            print(f"✅ Query successful!")
            print(f"   Total records in power_consumption table: {count}")
            
            return True, "Connection successful", count
            
    except Exception as e:
        error_msg = f"❌ Database connection failed: {type(e).__name__}"
        print(error_msg)
        print(f"   Details: {e}")
        
        # Provide helpful error messages for common issues
        if "password" in str(e).lower() or "authentication" in str(e).lower():
            print("\n💡 Tip: Check your database credentials in .env file")
        elif "could not connect" in str(e).lower() or "connection refused" in str(e).lower():
            print("\n💡 Tip: Ensure PostgreSQL is running and the server is accessible")
        elif "database" in str(e).lower() and "does not exist" in str(e).lower():
            print("\n💡 Tip: Create the database first: CREATE DATABASE powercast;")
        elif "relation" in str(e).lower() and "does not exist" in str(e).lower():
            print("\n💡 Tip: Create the table first by running database/schema.sql")
        
        import traceback
        traceback.print_exc()
        
        return False, error_msg, None


def get_database_engine():
    """
    Create and return a SQLAlchemy engine for database operations.
    
    Returns:
        sqlalchemy.Engine: Database engine
        
    Raises:
        ValueError: If DB_URL is not configured
    """
    db_url = os.getenv('DB_URL')
    
    if not db_url:
        raise ValueError("DB_URL not found in .env file. Please configure it first.")
    
    return create_engine(db_url)


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 CalPowerCast Database Connection Test")
    print("=" * 60)
    
    success, message, count = test_database_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Database connection test PASSED")
        if count is not None:
            if count == 0:
                print("⚠️  Warning: Table exists but is empty")
                print("   Run database/load_data.py to populate it")
            else:
                print(f"✅ Found {count} records in power_consumption table")
    else:
        print("❌ Database connection test FAILED")
        print(f"   {message}")
    print("=" * 60)

