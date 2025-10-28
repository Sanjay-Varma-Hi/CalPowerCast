"""
Quick test script to demonstrate the CalPowerCast API endpoints
Run this after starting the server with: python backend/app.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("🧪 Testing CalPowerCast API Endpoints\n")
    
    # 1. Test root endpoint
    print("1️⃣  Testing GET /")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 2. Test counties endpoint
    print("2️⃣  Testing GET /counties")
    response = requests.get(f"{BASE_URL}/counties")
    data = response.json()
    print(f"   Available counties: {', '.join(data['counties'])}\n")
    
    # 3. Test forecast endpoint
    print("3️⃣  Testing GET /forecast?county=Santa Clara&periods=6")
    response = requests.get(f"{BASE_URL}/forecast", params={"county": "Santa Clara", "periods": 6})
    data = response.json()
    print(f"   County: {data['county']}")
    print(f"   Periods: {data['periods']}")
    print(f"   First 3 predictions:")
    for pred in data['forecast'][:3]:
        print(f"      {pred['date']}: {pred['predicted_kwh']} kWh/household (range: {pred['lower_bound']} - {pred['upper_bound']})")
    print()
    
    # 4. Test error handling
    print("4️⃣  Testing error handling with invalid county")
    response = requests.get(f"{BASE_URL}/forecast", params={"county": "Invalid County"})
    print(f"   Status Code: {response.status_code}")
    print(f"   Error: {response.json()}\n")
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    try:
        test_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API. Is the server running?")
        print("   Start it with: cd backend && python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

