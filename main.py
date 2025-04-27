# from flask import Flask, request, jsonify
# import os
# import logging
import pandas as pd

from open_ai_helpers import *
from config import *
from prompts import *

input_sentence = '''
I live near Ward 5 Mary House 4303 13th st NE Washington DC 20017
'''



# logger : start service



# logger : llm1 call for feature extracton
llm1_output = get_completion(open_ai_api_key_2, 
                             prompt=extractor_llm_prompt(input_sentence),
                             model="gpt-3.5-turbo",
                             temperature=0.7
                             )['choices'][0]['message']['content']
print(llm1_output)





# logger : llm2 call for sql generation
df = pd.load_csv('data.csv')
filtered_df = df[(df['Region'] == llm1_output['region']) & (df['County'] == llm1_output['county'])]







# convert address to (lat, long)
lat, lon = lat_lon_finder(llm1_output['address'])

# find distance of this user with food centers
all_distances = dist_cal(lat, lon, filtered_df)

# find top 10 nearest locations
nearest_neighbours = []
for dist, display_addr in all_distances:
    nearest_neighbours.append((dist, display_addr))
    if len(nearest_neighbours) >= 10:
        break






# LLM call to analyse which of the top 10 are most elegible
llm2_output = get_completion(open_ai_api_key, 
                             prompt=summary_llm_prompt(input_sentence, llm1_output),
                             model="gpt-3.5-turbo",
                             temperature=0.7
                             )['choices'][0]['message']['content']
print(llm2_output)