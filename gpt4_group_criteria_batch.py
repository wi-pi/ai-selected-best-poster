"""
    Sample Usage:
        python gpt4_group_criteria_batch.py --image_dir "./images" --result_base_dir "./output_json_files"
"""

import argparse
import os
import time
from pathlib import Path

from gemini_utils import DEFAULT_MODEL, get_completion, load_json, parse_into_json, write_to_json

parser = argparse.ArgumentParser()
parser.add_argument('--image_dir', default="./images", type=str, help='Directory with poster images')
parser.add_argument('--result_base_dir', type=str, default="./output_json_files", help="Directory for storing the outputs")
parser.add_argument('--model', type=str, default=DEFAULT_MODEL, help="Gemini model name")
parser.add_argument('--num_runs', type=int, default=5, help="Number of scoring runs per poster")
args = parser.parse_args()

result_base_dir = args.result_base_dir
Path(result_base_dir).mkdir(parents=True, exist_ok=True)

criteria = load_json('./criteria.json')

for file in sorted(os.listdir(args.image_dir)):
    if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue
    file_path = os.path.join(args.image_dir, file)
    cleaned_filename = os.path.splitext(file)[0]
    print(f"Processing file: {file_path}")

    # One file per run, so finished runs are never repeated
    run_dir = Path(result_base_dir) / cleaned_filename
    run_dir.mkdir(parents=True, exist_ok=True)

    total_scores = []
    parsed_jsons = []

    for i in range(args.num_runs):
        print(f"Run {i+1}")
        run_path = run_dir / f"run{i+1}.json"

        if run_path.exists():
            parsed_json = load_json(run_path)
            print(f"Run {i+1} already done, skipping.")
        else:
            try:
                head_prompt = "Please rate the attached technical poster based on the specified criteria. Your task is to assign a score between 0 and 4, following these guidelines:"
                tail_prompt = """
                If you think a poster's performance is between 3-4, choose 4 if it closely meets the guidelines and 3 if it's closer to the next lower level.
                Similarly, for a performance between 1-2, choose 2 if it's close to meeting the guidelines and 1 if it's nearer to the lower level.
                Format your feedback as JSON formatted with the keys 'score' and 'explanation' for each criterion."""
                prompt = f"{head_prompt}\n{criteria}\n{tail_prompt}"
                parsed_json = parse_into_json(get_completion(prompt, file_path, model=args.model))
            except Exception as e:
                print(f"Error: {e}, failed to get a valid response.")
                continue

            if sum('score' in item for item in parsed_json.values()) != len(criteria):
                print(f"Error: Incorrect criteria count, expected {len(criteria)} criteria.")
                continue

            write_to_json(parsed_json, run_path)
            time.sleep(0.1)

        total_score = sum(int(item['score']) for item in parsed_json.values() if 'score' in item)
        for cr, item in parsed_json.items():
            print(f"{cr}: {item.get('score')} of 4")
        print(f"Total Score: {total_score} of {4*len(criteria)}")
        parsed_jsons.append(parsed_json)
        total_scores.append(total_score)

    if total_scores:
        average_score = sum(total_scores) / len(total_scores)
        print(f"AVERAGE SCORE for {cleaned_filename}: {average_score} of {4*len(criteria)}")
        write_to_json(parsed_jsons, f"{result_base_dir}/{cleaned_filename}.json")
