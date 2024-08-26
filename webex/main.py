from fastapi import FastAPI, HTTPException
import requests
import yaml

# Load the config file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

CHATBOT_BASEURL = config['webex']['base_url']
CHATBOT_PORT = config['webex']['port']
CHATBOT_URL = f'http://{CHATBOT_BASEURL}:{CHATBOT_PORT}/incoming'

app = FastAPI()

@app.get("/status")
async def get_status():
    return {"status": "Servidce is running----:" + CHATBOT_URL}

# Use a test room_id for testing
room_id = 'roomid-for-testing-here'

@app.post("/send_webex_message")
async def send_webex_message(message: str):
    payload = {
        "room_id": room_id,
        "message": message
    }
    
    # Send the POST request to the chatbot
    try:
        response = requests.post(CHATBOT_URL, json=payload)
        response.raise_for_status()
        return {"status": "message sent successfully"}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
