import requests

API_URL = "http://localhost:8000/api"

# Register
resp = requests.post(f"{API_URL}/auth/register", json={
    "email": "test@docuforge.ai",
    "password": "password123",
    "full_name": "Test User"
})

# Login
resp = requests.post(f"{API_URL}/auth/login", data={
    "username": "test@docuforge.ai",
    "password": "password123"
})
token = resp.json().get("access_token")

# Create Project
headers = {"Authorization": f"Bearer {token}"}
resp = requests.post(f"{API_URL}/process-input?text=Healthcare+App", headers=headers)
print("Create Project Response:", resp.status_code)
print(resp.json())
