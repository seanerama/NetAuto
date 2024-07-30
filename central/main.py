from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

services = {
    "webex": "http://webex:8000",
    "solarwinds": "http://solarwinds:8000",
    "servicenow": "http://servicenow:8000",
    "dnacenter": "http://dnacenter:8000",
    "sshscp": "http://sshscp:8000"
}

@app.get("/status/{service_name}")
def get_service_status(service_name: str):
    if service_name not in services:
        raise HTTPException(status_code=404, detail="Service not found")
    response = requests.get(f"{services[service_name]}/status")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching status")
    return response.json()

@app.post("/test/{service_name}")
def perform_test(service_name: str, data: dict):
    if service_name not in services:
        raise HTTPException(status_code=404, detail="Service not found")
    
    response = requests.post(f"{services[service_name]}/test", json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error With Test")
    
    return response.json()

@app.get("/test_dnac_login")
def test_dnac_login():
    response = requests.get(f"{services['dnacenter']}/test_dnac_login")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching DNAC login")
    return response.json()