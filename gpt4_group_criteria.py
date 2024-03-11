"""
    Sample Usage:
        python gpt4_group_criteria.py --image_path "./images/path_to_your_poster_file" --result_base_dir "./output_json_files"
"""

import argparse
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv
import openai
from openai import OpenAI
from pathlib import Path
import time
import os
import base64
import requests
import json
import numpy as np
_ = load_dotenv(find_dotenv()) # read local .env file and set OPENAI KEY
api_key = os.environ['OPENAI_API_KEY']

  
# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def load_json(json_path):
    with open(json_path) as fin:
        json_obj=json.load(fin)
    return json_obj
 
def convert_to_serializable(obj):
    if isinstance(obj, np.int64):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj
    
def parse_into_json(data_str):
        # Stripping the Markdown code block delimiters
    data_str = data_str.strip("'")
    data_str = data_str.replace('```json\n', '', 1)
    data_str = data_str.rsplit('\n```', 1)[0]

    # Parsing the JSON string
    parsed_json = json.loads(data_str)
    return parsed_json


def write_to_json(json_obj,json_path):
    with open(json_path,'w') as fout:
        json.dump(json_obj,fout,default=convert_to_serializable)


def get_completion(prompt,base64_image):
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }
    payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": prompt
                        },
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                        }
                    ]
                    }
                ],
                "max_tokens": 300
                }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response
    


#load the arguments
parser=argparse.ArgumentParser()
parser.add_argument('--image_path',default="./images/Teaching_Day_Poster_SL.png",type=str, help='Model Name for storing purposes: should match the directory Name')
parser.add_argument('--result_base_dir',type=str,default="./output_json_files",help="Directory for storing the outputs")
args=parser.parse_args()

# create the result directory
result_base_dir=args.result_base_dir
if not os.path.exists(result_base_dir):
    Path(result_base_dir).mkdir(parents=True, exist_ok=True)

# load the criteria json file
criteria=load_json(f'./criteria.json')

# loop through the criteria and get the scores
total_scores = 0
# pbar = tqdm(criteria)
#     pbar.set_description(f'Processing criteria {cr}')
for cr in criteria:
    try:
        head_prompt=f"Rate the attached technical poster on a scale of 0-2 based on {cr}. The guidelines for the scores are:"
        guidelines=criteria[cr]
        tail_prompt=f"I want the output in a JSON format with the keys 'score' and 'explanation'"
        prompt=f"{head_prompt}\n{guidelines}\n{tail_prompt}"
        response=get_completion(prompt=prompt, base64_image=encode_image(args.image_path))
        # response_json=json.loads(response.json())
        response_json=response.json()
        output_dict=response_json['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error: {e}, failed to retrieve response json file.\n Criteria: {cr},\n Response: {response.json()}")
        continue

    # Stripping the Markdown code block delimiters and parse into JSON
    parsed_json = parse_into_json(output_dict)

    score = int(parsed_json['score'])
    explanation = parsed_json['explanation']
    total_scores += score
    print(f"Criteria: {cr},\n Score: {score},\n Explanation: {explanation}")

    time.sleep(0.1)
    
    write_to_json(parsed_json,f'{result_base_dir}/{cr}_score_with_explanation.json')

print(f"Total Score: {total_scores} of 14.")
