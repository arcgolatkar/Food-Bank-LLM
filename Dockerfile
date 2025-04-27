FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PORT=5000

EXPOSE 5000

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"] 