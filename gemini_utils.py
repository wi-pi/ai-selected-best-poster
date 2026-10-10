"""Shared Gemini (AI Studio) helpers for the poster scoring scripts."""

import json
import mimetypes
import os

import backoff
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import errors, types

_ = load_dotenv(find_dotenv())  # read local .env file and set GEMINI_API_KEY
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

DEFAULT_MODEL = "gemini-3.1-pro-preview"

# The system prompt is passed through system_instruction, not as a user message.
SYSTEM_PROMPT = (
    "You are an expert judge of scientific and technical posters. "
    "Score the attached poster strictly against the provided rubric guidelines "
    "and reply only with valid JSON in the requested format."
)


def load_json(json_path):
    with open(json_path) as fin:
        return json.load(fin)


def write_to_json(json_obj, json_path):
    with open(json_path, "w") as fout:
        json.dump(json_obj, fout)


def parse_into_json(data_str):
    data_str = data_str.strip().strip("'")
    if data_str.startswith("```"):
        data_str = data_str.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(data_str)


def _retryable(e):
    # Retry rate limits and server errors only.
    return isinstance(e, errors.APIError) and (e.code == 429 or (e.code or 0) >= 500)


@backoff.on_exception(backoff.expo, errors.APIError, max_tries=6, giveup=lambda e: not _retryable(e))
def get_completion(prompt, image_path, model=DEFAULT_MODEL, max_output_tokens=8192):
    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        image_part = types.Part.from_bytes(data=f.read(), mime_type=mime)
    response = client.models.generate_content(
        model=model,
        contents=[image_part, prompt],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            max_output_tokens=max_output_tokens,
        ),
    )
    return response.text
