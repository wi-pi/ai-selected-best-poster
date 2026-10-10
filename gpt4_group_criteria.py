"""
    Sample Usage:
        python gpt4_group_criteria.py --image_path "./images/path_to_your_poster_file" --result_base_dir "./output_json_files"
"""

import argparse
import os
import time
from pathlib import Path

from gemini_utils import DEFAULT_MODEL, get_completion, load_json, parse_into_json, write_to_json

parser = argparse.ArgumentParser()
parser.add_argument('--image_path', default="./images/Teaching_Day_Poster_SL.png", type=str, help='Path to the poster image')
parser.add_argument('--result_base_dir', type=str, default="./output_json_files", help="Directory for storing the outputs")
parser.add_argument('--model', type=str, default=DEFAULT_MODEL, help="Gemini model name")
parser.add_argument('--num_runs', type=int, default=5, help="Number of scoring runs per poster")
args = parser.parse_args()

result_base_dir = args.result_base_dir
Path(result_base_dir).mkdir(parents=True, exist_ok=True)

criteria = load_json('./criteria.json')

total_scores = []
for i in range(args.num_runs):
    print(f"Run {i+1}")
    total_score = 0
    for cr in criteria:
        out_path = f"{result_base_dir}/{'_'.join(cr.split())}_score_with_explanation_run{i+1}.json"
        # Skip work that is already done
        if os.path.exists(out_path):
            score = int(load_json(out_path)['score'])
            total_score += score
            print(f"Criteria: {cr}, already done (score {score}), skipping.")
            continue

        try:
            head_prompt = f"Please rate the attached technical poster based on the specified criteria '{cr}'. Your task is to assign a score between 0 and 4, following these guidelines:"
            guidelines = criteria[cr]
            tail_prompt = """
            If you think a poster's performance is between 3-4, choose 4 if it closely meets the guidelines and 3 if it's closer to the next lower level.
            Similarly, for a performance between 1-2, choose 2 if it's close to meeting the guidelines and 1 if it's nearer to the lower level.
            Format your feedback as JSON format with the keys 'score' and 'explanation'"""
            prompt = f"{head_prompt}\n{guidelines}\n{tail_prompt}"
            parsed_json = parse_into_json(get_completion(prompt, args.image_path, model=args.model))
            score = int(parsed_json['score'])
        except Exception as e:
            print(f"Error: {e}, failed to get a valid response.\n Criteria: {cr}")
            continue

        total_score += score
        print(f"Criteria: {cr},\n Score: {score},\n Explanation: {parsed_json['explanation']}")
        write_to_json(parsed_json, out_path)
        time.sleep(0.1)

    print(f"Total Score: {total_score} of {4*len(criteria)}")
    total_scores.append(total_score)

average_score = sum(total_scores) / args.num_runs
print(f"Average Score: {average_score} of {4*len(criteria)}")
