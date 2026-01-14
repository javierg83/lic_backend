import requests
import json

BASE_URL = "http://localhost:8000"

def test_login(username, password, description):
    print(f"\n--- Testing {description} ---")
    data = {"username": username, "password": password}
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    # Test valid login
    test_login("usuario", "password", "Valid Credentials")
    
    # Test invalid login (should be 401 now)
    test_login("usuario", "wrong_password", "Invalid Credentials")
    
    # Test non-existent route (should be handle by 404 redirect unless it's POST)
    print("\n--- Testing 404 Post ---")
    try:
        response = requests.post(f"{BASE_URL}/non-existent")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
         print(f"Error connecting: {e}")
