import requests
import json

def test_api():
    # Base URL
    base_url = 'http://localhost:5000'
    
    # Start a session to maintain cookies
    s = requests.Session()
    
    # First login
    login_data = {
        'email': 'test@example.com',
        'password': 'testpassword'
    }
    
    print("\n1. Testing login...")
    login_response = s.post(f'{base_url}/login', data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    # Test get_available_doctors
    print("\n2. Testing get_available_doctors...")
    doctors_response = s.get(f'{base_url}/get_available_doctors')
    print(f"Status: {doctors_response.status_code}")
    print(f"Response: {doctors_response.text}")
    
    # Test request_approval
    print("\n3. Testing request_approval...")
    approval_data = {
        'diagnosis_id': 'test_diagnosis',
        'doctor_id': 'test_doctor'
    }
    approval_response = s.post(f'{base_url}/request_approval', data=approval_data)
    print(f"Status: {approval_response.status_code}")
    print(f"Response: {approval_response.text}")

if __name__ == '__main__':
    test_api() 