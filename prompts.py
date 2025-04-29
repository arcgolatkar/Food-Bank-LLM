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
6. Geo_Address : address given in the input but in a specific format i.e. <street_number> <stree_name> <region> <pincode>. Return type is string. If empty then return empty string.
</tasks>



*** Output Format ***
Make sure your output is in JSON format and if you dont find any of the field then return empty
string for it
<output>
    "address" : "Kingdom Care Center 11700 Beltsville Drive Beltsville Prince George's County MD 20705",
    "region" : "MD",
    "county" : "Prince George's County",
    "day" : "Thursday",
    "distribution_mode" : "",
    "geo_address" : "11700 Beltsville Drive Beltsville MD 20705"
</output>


** Example Input **
I live near Manassas City Mary Bull Run Unitarian Universalists 9350 Main 
Street Manassas VA 20110 and I want to go to a food distribution center on Fridays only and I can only go
via walking.

** Example Output **
{   'address': 'Ward 5 Mary House 4303 13th st NE Washington DC 20017', 
    'region': 'DC', 
    'county': 'Ward 5', 
    'day': 'Friday', 
    'distribution_mode': 'Walk Up', 
    'geo_address': '4303 13th st NE Washington DC 20017'
}


*** Now can you do this for this input sentence ***
{input_sentence}

'''


def summary_llm_prompt(input_sentence, llm1_output, nearest_neighbours):
    return f''' 
    
    given following input sentence : 
    <input>{input_sentence}</input>

    And following extracted information from the input sentence : 
    <extracted_info>{llm1_output}</extracted_info>

    You are also provided with some closest food stores near the input address and some information about these food stores : 
    <nearest_neighbours>{nearest_neighbours}</nearest_neighbours>

    Your task is to recommend top 5 (OR LESS i.e. HOWMUCH EVER FITS THE CRITERIA) food stores from the given list which <IMP>fits all the criterias given in the input sentence</IMP>.
    For instance if the input sentence says 'I need food every Monday' then you need to find the food stores which are open on Monday only and so on.

    Output the recommendations in such a format that it is readable, uses emojis and well formatted. 
    Give important information about the food store like its 
    - address 
    - contact details 
    - what ids you need to bring 
    - start time and end time
    - distribution mode
    - other important information

    If you find any of the information missing then dont include it in the output.


    <>Sample Output<>
    Based on your location and preferences, here are the food distribution centers that you can visit:

    1. 🏠 **Mary House - Ward 5**  
    - 📍 Address: 4303 13th st NE Washington DC 20017
    - 📞 Contact: (202) 635-9025
    - 🕒 Time: Tuesday, 1st and 3rd of the Month, 10:00 AM - 01:00 PM
    - 🚗 Distribution Mode: Home Delivery, Walk up

    2. 🏠 **Northeastern Presbyterian Church**  
    - 📍 Address: 2112 Varnum St. NE Washington DC 20018
    - 📞 Contact: (202) 316-8744
    - 🕒 Time: Saturday, 3rd of the Month, 10:00 AM - 12:00 PM
    - 🚶‍♂️ Distribution Mode: Walk up

    3. 🏠 **McKendree-Simms-Brookland United Methodist Church**  
    - 📍 Address: 2411 Lawrence St NE Washington DC 20018
    - 📞 Contact: (202) 526-3685
    - 🕒 Time: Friday, Tuesday, 10:00 AM - 02:00 PM
    - 🆔 ID Required: Yes, Zip Code
    - 🚶‍♂️ Distribution Mode: Walk up (Only for Ward Five residents)

    4. 🏠 **Metropolis Club**  
    - 📍 Address: 938 Rhode Island Ave NE Washington DC 20018
    - 📞 Contact: (301) 793-4236
    - 🕒 Time: Friday, Monday, Saturday, Sunday, Thursday, Tuesday, Wednesday, 07:00 AM - 08:00 PM
    - 🚶‍♂️ Distribution Mode: Walk up

    5. 🏠 **Plenty to Eat**  
    - 📍 Address: 2315 18th Place NE Washington DC 20018
    - 📞 Contact: (202) 556-0662
    - 🕒 Time: Tuesday, Wednesday, 11:00 AM - 03:00 PM
    - 🆔 ID Required: Yes, Zip Code
    - 🚶‍♂️ Distribution Mode: Walk up
    '''