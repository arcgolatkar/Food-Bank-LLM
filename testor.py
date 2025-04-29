from main import *
import json

result = food_llm(
    # '''I live near Ward 5 Mary House 4303 13th st NE Washington DC 20017 and I want to go to a food distribution center on Thursdays only.'''
    '''I live near Manassas City Mary Bull Run Unitarian Universalists 9350 Main Street Manassas VA 20110 and I want to go to a food distribution center on Fridays only.'''
)

print(result)

# Print beautified JSON output
print(result['summary_llm_output'])