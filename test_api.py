import requests
import json
import time

def test_api():
    """Test the insurance prediction API"""
    
    # API base URL
    base_url = "http://localhost:5000"
    
    print("Testing Insurance Prediction API")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Health check passed: {result}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Health check error: {e}")
    
    # Test 2: Prediction with sample data
    print("\n2. Testing prediction endpoint...")
    
    test_cases = [
        {
            "name": "Young non-smoker",
            "data": {
                "age": 25,
                "sex": "female",
                "bmi": 22.0,
                "children": 0,
                "smoker": "no",
                "region": "southwest"
            }
        },
        {
            "name": "Older smoker",
            "data": {
                "age": 45,
                "sex": "male",
                "bmi": 35.0,
                "children": 2,
                "smoker": "yes",
                "region": "northeast"
            }
        },
        {
            "name": "Family with children",
            "data": {
                "age": 35,
                "sex": "female",
                "bmi": 28.5,
                "children": 3,
                "smoker": "no",
                "region": "southeast"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']}")
        try:
            response = requests.post(
                f"{base_url}/predict",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"   ✓ Prediction successful: ₹{result['predicted_charges_inr']:,.2f} (${result['predicted_charges_usd']:,.2f} USD)")
                else:
                    print(f"   ✗ Prediction failed: {result['message']}")
            else:
                print(f"   ✗ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    # Test 3: Invalid data
    print("\n3. Testing invalid data handling...")
    invalid_data = {
        "age": "invalid",
        "sex": "unknown",
        "bmi": -5,
        "children": "many",
        "smoker": "maybe",
        "region": "mars"
    }
    
    try:
        response = requests.post(
            f"{base_url}/predict",
            json=invalid_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            result = response.json()
            print(f"✓ Invalid data properly rejected: {result['message']}")
        else:
            print(f"✗ Invalid data not properly handled: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error testing invalid data: {e}")
    
    print("\n" + "=" * 40)
    print("API testing completed!")

if __name__ == "__main__":
    # Wait a moment for the server to start if needed
    print("Make sure the Flask server is running on http://localhost:5000")
    print("You can start it with: python app.py")
    print("\nWaiting 3 seconds before testing...")
    time.sleep(3)
    
    test_api() 