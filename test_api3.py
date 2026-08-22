import requests
API_URL = "http://localhost:8001/api"
resp = requests.post(f"{API_URL}/auth/login", data={"username": "test@docuforge.ai", "password": "password123"})
token = resp.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}
resp = requests.post(f"{API_URL}/process-input?text=Healthcare+App", headers=headers)
print("Response:", resp.status_code)
