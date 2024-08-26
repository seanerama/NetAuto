# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dnsutils for nslookup and other DNS tools
RUN apt-get update && apt-get install -y dnsutils iputils-ping

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Command to run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
