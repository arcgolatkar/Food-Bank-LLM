from flask import Flask, request, jsonify
import os
import logging
import pandas as pd

from open_ai_helpers import *
from helper import lat_lon_finder, dist_cal
from config import *
from prompts import *

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

def food_llm(input_sentence):



    # logger : start service
    # logger.info(f"Processing input: {input_sentence}")






    # logger : llm1 call for feature extraction
    try:
        llm1_output = get_completion(open_ai_api_key_2, 
                                prompt=extractor_llm_prompt(input_sentence),
                                model="gpt-3.5-turbo",
                                temperature=0.7
                                )['choices'][0]['message']['content']
        # logger.info("Feature extraction completed successfully")
    except Exception as e:
        # logger.error(f"Error in feature extraction: {str(e)}")
        return {"error": "Feature extraction failed", "details": str(e)}








    # logger : llm2 call for sql generation
    try:
        df = pd.read_csv('data.csv')
        filtered_df = df[(df['Region'] == llm1_output['region']) & (df['County'] == llm1_output['county'])]
        sql_command = f'''SELECT *
        FROM food_table
        WHERE REGION = '{llm1_output['region']}'
        AND COUNTY = '{llm1_output['county']}'
        '''
        # logger.info("SQL generation completed successfully")
    except Exception as e:
        # logger.error(f"Error in SQL generation: {str(e)}")
        return {"error": "SQL generation failed", "details": str(e)}






    # convert address to (lat, long)
    try:
        lat, lon = lat_lon_finder(llm1_output['address'])
        if lat is None or lon is None:
            # logger.warning("Could not geocode the address")
            return {"error": "Could not geocode the address"}
    except Exception as e:
        # logger.error(f"Error in geocoding: {str(e)}")
        return {"error": "Geocoding failed", "details": str(e)}





    # find distance of this user with food centers
    try:
        all_distances = dist_cal(lat, lon, filtered_df)
        
        # find top 10 nearest locations
        nearest_neighbours = []
        for dist, display_addr in all_distances:
            nearest_neighbours.append((dist, display_addr))
            if len(nearest_neighbours) >= 10:
                break
        # logger.info(f"Found {len(nearest_neighbours)} nearest locations")
    except Exception as e:
        # logger.error(f"Error in distance calculation: {str(e)}")
        return {"error": "Distance calculation failed", "details": str(e)}






    # LLM call to analyse which of the top 10 are most elegible
    try:
        llm2_output = get_completion(open_ai_api_key, 
                                prompt=summary_llm_prompt(input_sentence, llm1_output),
                                model="gpt-3.5-turbo",
                                temperature=0.7
                                )['choices'][0]['message']['content']
        # logger.info("Summary generation completed successfully")
    except Exception as e:
        # logger.error(f"Error in summary generation: {str(e)}")
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