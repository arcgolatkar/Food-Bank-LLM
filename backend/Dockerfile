# Use slim Python base image
FROM python:3.10-slim

# Set working directory inside the container
# This is where our app code will be copied
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y gcc libpq-dev curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
# apt-get update: Updates the package list.
# gcc => installing C compiler
# libpq-dev => installing PostgreSQL development library 
# curl => installling command-line tool 
#apt-get clean && rm -rf /var/lib/apt/lists/*: Cleans up cached files to reduce the image size.

# copyt requirements.txt file into the container
COPY requirements.txt . 

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files into the container
COPY . .

# Expose Flask app port
EXPOSE 5000

# Start app using Gunicorn (pointing to your main file and app name)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
