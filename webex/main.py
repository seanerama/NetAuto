from fastapi import FastAPI

app = FastAPI()

@app.get("/status")
async def get_status():
    return {"status": "Service is running"}

# Add specific endpoints for the service here
