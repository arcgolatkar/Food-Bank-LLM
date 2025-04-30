# Use slim Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y gcc libpq-dev curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files into the container
COPY . .

# Expose Flask app port
EXPOSE 5000

# Start app using Gunicorn (pointing to your main file and app name)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
