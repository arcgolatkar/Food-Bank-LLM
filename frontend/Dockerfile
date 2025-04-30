# ---- Base image ----
FROM python:3.10-slim

# ---- Set working directory ----
WORKDIR /app

# ---- Install system dependencies (for requests & streamlit) ----
RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# ---- Install Python packages ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy your Streamlit app code ----
COPY . .

# ---- Expose default Streamlit port ----
EXPOSE 8501

# ---- Run Streamlit ----
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
