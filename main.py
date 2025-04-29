from flask import Flask, request, jsonify
import os
import logging

from open_ai_helpers import *
from helper import lat_lon_finder, dist_cal
from prompts import *
import csv


#pip install --upgrade httpx openai



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

def food_llm(input_sentence):



    # logger : start service
    logger.info(f"Processing input: {input_sentence}")






    # feature extraction LLM
    try:
        # llm1_output = get_completion(prompt = extractor_llm_prompt(input_sentence))
        llm1_output = {
                            "address": "Ward 5 Mary House 4303 13th st NE Washington DC 20017",
                            "region": "DC",
                            "county": "Ward 5",
                            "day": "",
                            "distribution_mode": "",
                            "geo_address": "4303 13th st NE Washington DC 20017"
                        }
        logger.info("Feature extraction completed successfully")
    except Exception as e:
        logger.error(f"Error in feature extraction: {str(e)}")
        return {"error": "Feature extraction failed", "details": str(e)}







    # Sql generation LLM
    try:
        filtered_df = []
        with open('data.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Region'] == llm1_output['region'] and row['Zone'].replace(" ", "") == llm1_output['county'].replace(" ", ""):
                        filtered_df.append(row)

        if not filtered_df:
            return {"error": "No matching records found in the dataset"}

        sql_command = f'''SELECT *
        FROM food_table
        WHERE REGION = '{llm1_output['region']}'
        AND COUNTY = '{llm1_output['county']}'
        '''
        logger.info("SQL generation completed successfully")
    except Exception as e:
        logger.error(f"Error in SQL generation: {str(e)}")
        return {"error": "SQL generation failed", "details": str(e)}





    # convert address to (lat, long)
    try:
        lat, lon = lat_lon_finder(llm1_output['geo_address'])
        if lat is None or lon is None:
            logger.warning("Could not geocode the address")
            return {"error": "Could not geocode the address"}
    except Exception as e:
        logger.error(f"Error in geocoding: {str(e)}")
        return {"error": "Geocoding failed", "details": str(e)}





    # find distance of this user with food centers
    try:
        all_distances = dist_cal(lat, lon, filtered_df)
        
        # find top 10 nearest locations
        nearest_neighbours = []
        for i in all_distances:
            nearest_neighbours.append(i)
            if len(nearest_neighbours) >= 10:
                break
        logger.info(f"Found {len(nearest_neighbours)} nearest locations")
    except Exception as e:
        logger.error(f"Error in distance calculation: {str(e)}")
        return {"error": "Distance calculation failed", "details": str(e)}




    # LLM call to analyse which of the top 10 are most elegible
    # instead use embedding search in presentation
    try:
        llm2_output = get_completion( prompt=summary_llm_prompt(input_sentence, llm1_output, nearest_neighbours),
                                    model="gpt-4.1")   
        logger.info("Summary generation completed successfully")
    except Exception as e:
        logger.error(f"Error in summary generation: {str(e)}")
        return {"error": "Summary generation failed", "details": str(e)}







    return {
        'feature_extractor_llm_output': llm1_output,
        'coder_llm_output': sql_command,
        'nearest_locations': nearest_neighbours,
        'summary_llm_output': llm2_output
    }






@app.route('/api/process', methods=['POST'])
def process_input():
    """
    API endpoint to process user input and find food banks
    Expects JSON with "input" field containing the user query
    """
    try:
        data = request.json
        if not data or 'input' not in data:
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








if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)