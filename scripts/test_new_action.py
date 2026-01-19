import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000/demo/new"

def test_new_action_success():
    payload = {
        "nombre": "Juan Perez",
        "telefono": "123456789",
        "fecha_nacimiento": "1990-01-01",
        "edad": 36
    }
    # Nota: Hoy es 2026-01-14. 2026 - 1990 = 36.
    
    print(f"Testing success case with payload: {payload}")
    try:
        response = requests.post(BASE_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error connecting to server: {e}. Make sure the server is running.")

def test_new_action_validation_error():
    payload = {
        "nombre": "Juan Perez",
        "telefono": "123456789",
        "fecha_nacimiento": "1990-01-01",
        "edad": 25 # Edad incorrecta
    }
    
    print(f"\nTesting validation error with payload: {payload}")
    try:
        response = requests.post(BASE_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    test_new_action_success()
    test_new_action_validation_error()
