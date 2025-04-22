# Start from a slim Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Tell Cloud Run to listen on the port it provides in $PORT
# and start your Flask app via Gunicorn, allowing for long (up to 15m) requests
CMD ["sh", "-c", "gunicorn routes:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 900"]
