def extractor_llm_prompt(input_sentence):
    return f'''

Assume you are an expert in extracting keywords from the given input. You task is to extract \n
following fields from the given sentence.



*** Input Sentence ***
<input> 
I live near 'Kingdom Care Center 11700 Beltsville Drive Beltsville Prince George's County MD 20705', \n
find me some place where I can go every Thursady to get food
</input>



*** Tasks ***
You are tasked to extract following information from the <input>
<tasks>
1. Address : address given in the input. Return type is string. If empty then return empty string.
2. Region : from the address you need to figure out if it belongs to any of the following regions
            ['DC', 'MD', 'VA']. Return type is string. If empty then return empty string.
3. County : from the address you need to figure out if it belongs to any of the following counties
            ['Outside CAFB Service Area','Ward 1', 'Ward 2', 'Ward 3', 'Ward 4', 'Ward 5', 'Ward 6', 'Ward 7', 'Ward 8', 
            'Montgomery County', 'Prince George's County', 'Arlington County', 'City of Alexandria', 'City of Manassas', 
            'Fairfax County', 'Falls Church City', 'Manassas City', 'Prince William County']. Return type is string. 
            If empty then return empty string.
4. Day of Week : it can be one of the following ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].
                 Return type is string. If empty then return empty string.
5. Distribution Mode : it can be following (can be multiple too) ['Drive Through', 'Home Delivery', 'Walk Up']. 
                        Return type is string. If empty then return empty string. If multiple then return a list of strings.
</tasks>



*** Output Format ***
Make sure your output is in JSON format and if you dont find any of the field then return empty
string for it
<output>
    "address" : "Kingdom Care Center 11700 Beltsville Drive Beltsville Prince George's County MD 20705",
    "region" : "MD",
    "county" : "Prince George's County",
    "day" : "Thursday",
    "distribution_mode" : ""
</output>

*** Now can you do this for this input sentence ***
{input_sentence}

'''


def summary_llm_prompt(input_sentence):
    return f''' '''