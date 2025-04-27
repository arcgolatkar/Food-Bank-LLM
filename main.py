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
llm1_output = get_completion(open_ai_api_key, 
                             prompt=extractor_llm_prompt(input_sentence),
                             model="gpt-3.5-turbo",
                             temperature=0.7
                             )['choices'][0]['message']['content']
print(llm1_output)




# logger : llm2 call for sql generation
df = pd.load_csv('CAFB_Shopping_Partners_Data.csv')
filtered_df = df[(df['Region'] == llm1_output['region']) & (df['County'] == llm1_output['county'])]
unique_addresses = filtered_df['Address'].unique()
print(unique_addresses)


# jeolat to find top 10 nearest locations
#top_5_nearest = nearest_finder(input, surrounding_places)


# LLM call to analyse which of the top 10 are most elegible
llm2_output = get_completion(open_ai_api_key, 
                             prompt=summary_llm_prompt(input_sentence, llm1_output),
                             model="gpt-3.5-turbo",
                             temperature=0.7
                             )['choices'][0]['message']['content']
print(llm2_output)