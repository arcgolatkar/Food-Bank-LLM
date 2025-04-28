# Food Bank LLM API

This is a Flask-based API that helps users find nearby food banks based on their location and needs.

## API Endpoints

### 1. Process Input (`/api/process`)
- **Method**: POST
- **Description**: Processes user input to find relevant food banks
- **Request Body**:
  ```json
  {
    "input": "I need help finding food banks near 123 Main St, New York"
  }
  ```
- **Response**: 
  ```json
  {
    "feature_extractor_llm_output": { /* Extracted features */ },
    "coder_llm_output": "SQL query",
    "nearest_locations": [ /* List of nearby locations */ ],
    "summary_llm_output": "Summary text"
  }
  ```

### 2. Health Check (`/api/health`)
- **Method**: GET
- **Description**: Confirms the API is running properly
- **Response**:
  ```json
  {
    "status": "healthy"
  }
  ```

### 3. Home (`/`)
- **Method**: GET
- **Description**: Provides basic API information
- **Response**: 
  ```json
  {
    "message": "Food Bank LLM API",
    "endpoints": {
      "/api/process": "POST - Process text input to find nearby food banks",
      "/api/health": "GET - Health check"
    }
  }
  ```

## Running the API

### Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Flask app:
   ```
   python main.py
   ```
   
3. The API will be available at `http://localhost:5000`

### Using Docker

1. Build the Docker image:
   ```
   docker build -t food-bank-llm .
   ```

2. Run the container:
   ```
   docker run -p 5000:5000 food-bank-llm
   ```

3. The API will be available at `http://localhost:5000`

