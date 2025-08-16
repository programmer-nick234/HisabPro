import requests
import json

def test_login():
    base_url = 'http://127.0.0.1:8000/api'
    
    # Test login endpoint
    login_url = f'{base_url}/auth/login/'
    
    # Test credentials
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    print("Testing login endpoint...")
    print(f"URL: {login_url}")
    print(f"Data: {login_data}")
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"User: {data.get('user', {}).get('username', 'N/A')}")
            print(f"Tokens received: {'access' in data.get('tokens', {})}")
        else:
            print("❌ Login failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Backend server not running!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
