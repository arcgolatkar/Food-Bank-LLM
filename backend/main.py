from flask import Flask, request, jsonify
import os
import logging
import json
from open_ai_helpers import *
from helper import lat_lon_finder, dist_cal
from prompts import *
import csv
import watchtower

# =================== Configure CloudWatch Logging ===================

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if os.getenv('AWS_REGION'):
    logger.addHandler(watchtower.CloudWatchLogHandler(
        log_group=os.getenv('CLOUDWATCH_LOG_GROUP', 'FoodBankLLMLogs'),
        stream_name=os.getenv('CLOUDWATCH_STREAM_NAME', 'BackendStream'),
        create_log_group=True
    ))
else:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.info("Flask App and Logging Initialized.")

# =================== Initialize Flask App ===================

app = Flask(__name__)

# =================== Core Processing Logic ===================

import json

def food_llm(input_sentence: str) -> dict:
    logger.info(f"Processing input: {input_sentence}")

    # Step 1: Feature Extraction (LLM1)
    try:
        llm1_response = get_completion(prompt=extractor_llm_prompt(input_sentence),key=os.getenv('OPENAI_API_KEY'))
        llm1_raw_output = llm1_response.choices[0].message.content

        logger.info(f"LLM1 raw output: {llm1_raw_output}")

        try:
            llm1_output = json.loads(llm1_raw_output)
        except Exception as e:
            logger.error(f"Failed to parse LLM1 output as JSON: {e}")
            return {"error": "Failed to parse feature extraction output", "details": str(e)}

        # Validate expected fields
        required_fields = ["address", "region", "county", "geo_address"]
        if not all(field in llm1_output for field in required_fields):
            logger.error(f"Missing fields in extracted output: {llm1_output}")
            return {"error": "Missing required fields in extracted information"}
        
        logger.info("Feature extraction completed successfully")

    except Exception as e:
        logger.error(f"Error during feature extraction: {str(e)}")
        return {"error": "Feature extraction failed", "details": str(e)}

    # Step 2: Filter Data from CSV
    try:
        filtered_df = []
        with open('data.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Region'] == llm1_output['region'] and row['Zone'].replace(" ", "") == llm1_output['county'].replace(" ", ""):
                    filtered_df.append(row)

        if not filtered_df:
            logger.warning("No matching records found in dataset.")
            return {"error": "No matching records found in the dataset"}

        sql_command = f"""
        SELECT * FROM food_table
        WHERE REGION = '{llm1_output['region']}'
        AND COUNTY = '{llm1_output['county']}'
        """
        
        logger.info("SQL command generated successfully")

    except Exception as e:
        logger.error(f"Error during SQL generation: {str(e)}")
        return {"error": "SQL generation failed", "details": str(e)}

    # Step 3: Geocoding
    try:
        lat, lon = lat_lon_finder(llm1_output['geo_address'])
        if lat is None or lon is None:
            logger.warning(f"Could not geocode address: {llm1_output['geo_address']}")
            return {"error": "Address too ambiguous or incomplete to geocode. Please provide a full address with street, city, and zip code."}
        
        logger.info(f"Geocoded address to coordinates: ({lat}, {lon})")

    except Exception as e:
        logger.error(f"Error during geocoding: {str(e)}")
        return {"error": "Geocoding failed", "details": str(e)}

    # Step 4: Distance Calculation
    try:
        all_distances = dist_cal(lat, lon, filtered_df)
        nearest_neighbours = all_distances[:10]

        if not nearest_neighbours:
            logger.warning("No nearby locations found after distance calculation.")
            return {"error": "No nearby food centers found"}

        logger.info(f"Found {len(nearest_neighbours)} nearest centers")

    except Exception as e:
        logger.error(f"Error during distance calculation: {str(e)}")
        return {"error": "Distance calculation failed", "details": str(e)}

    # Step 5: Summary using LLM2
    try:
        llm2_response = get_completion(prompt=summary_llm_prompt(input_sentence, llm1_output, nearest_neighbours), model="gpt-4.1",key=os.getenv('OPENAI_API_KEY'))
        llm2_summary = llm2_response.choices[0].message.content

        logger.info("Summary generation completed successfully")

    except Exception as e:
        logger.error(f"Error during summary generation: {str(e)}")
        return {"error": "Summary generation failed", "details": str(e)}

    # Step 6: Return Successful Output
    return {
        "feature_extractor_llm_output": llm1_output,
        "coder_llm_output": sql_command,
        "nearest_locations": nearest_neighbours,
        "summary_llm_output": llm2_summary,
        "status": "success"
    }

# =================== API Routes ===================

@app.route('/api/process', methods=['POST'])
def process_input():
    try:
        data = request.json
        if not data or 'input' not in data:
            logger.warning("Missing 'input' field in request body.")
            return jsonify({"error": "Missing 'input' field in request"}), 400
        
        input_text = data['input']
        result = food_llm(input_text)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

# =================== App Runner ===================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
