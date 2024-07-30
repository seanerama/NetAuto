from fastapi import FastAPI
import yaml


# Load the config file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
app = FastAPI()

usr = config['network_devices']['cli_username']
cli_pw = config['network_devices']['cli_password']


@app.get("/status")
async def get_status():
    return {"status": "Service is running"}


@app.post("/test")
async def test(data: dict):
    return data, usr, cli_pw

# Add specific endpoints for the service here

