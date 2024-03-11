#  The AI-selected “best” poster award

This script, `gpt4_group_criteria.py`, is a Python script that uses OpenAI's GPT-4V model to perform certain tasks. The script requires an OpenAI API key to function.

## Criteria

The script uses the following criteria:

- Organization
- Graphics
- Data Visualization
- Text
- White Space
- Objectives
- Main Points

## How to Use

1. Ensure you have a `.env` file in your project root with your OpenAI API key. The key should be stored as `OPENAI_API_KEY=your_api_key_here`.

2. Use the script by running the command `python gpt4_group_criteria.py --image_path "./images/path_to_your_poster_file" --result_base_dir "./output_json_files"`. Replace `./images/path_to_your_poster_file` with the path to the image you want to encode, and `./output_json_files` with the directory where you want to store the output JSON files.

## Functions

### `encode_image(image_path)`

This function takes an image path as input and returns the base64 encoding of the image.

### `load_json(json_path)`

This function takes a JSON file path as input and returns the loaded JSON object.

### `convert_to_serializable(obj)`

This function takes a numpy object as input and converts it into a serializable format. It supports `np.int64` and `np.ndarray` objects.