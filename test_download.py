import requests
import os

API_URL = "http://localhost:8000/api"

# Login to get token
login_resp = requests.post(f"{API_URL}/auth/login", data={"username": "test@docuforge.ai", "password": "password123"})
if login_resp.status_code != 200:
    print(f"Login failed: {login_resp.text}")
    exit(1)

token = login_resp.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Get projects to find one
projects_resp = requests.get(f"{API_URL}/projects", headers=headers)
projects = projects_resp.json()
if not projects:
    print("No projects found to test download")
    exit(1)

project_id = projects[0]["id"]
print(f"Testing download for project {project_id}...")

# Test DOCX
docx_url = f"{API_URL}/documents/download/{project_id}/srs/docx"
docx_resp = requests.get(docx_url, headers=headers)
print(f"DOCX status: {docx_resp.status_code}")
if docx_resp.status_code == 200:
    print(f"DOCX size: {len(docx_resp.content)} bytes")
else:
    print(f"DOCX Error: {docx_resp.text}")

# Test PDF
pdf_url = f"{API_URL}/documents/download/{project_id}/srs/pdf"
pdf_resp = requests.get(pdf_url, headers=headers)
print(f"PDF status: {pdf_resp.status_code}")
if pdf_resp.status_code == 200:
    print(f"PDF size: {len(pdf_resp.content)} bytes")
else:
    print(f"PDF Error: {pdf_resp.text}")

