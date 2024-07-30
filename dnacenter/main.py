from fastapi import FastAPI
import dnac_apis

app = FastAPI()

@app.get("/status")
async def get_status():
    return {"status": "Service is running"}

@app.get("/test_dnac_login")
async def test_dnac_login():
    token = dnac_apis.get_dna_center_token()
    return token


# Add specific endpoints for the service here
