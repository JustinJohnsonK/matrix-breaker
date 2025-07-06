# AI controller logic

from flask import request, jsonify
from utils.firebase_auth import firebase_auth_required
import requests
from config import load_config
import json
import logging

_config = load_config()
OLLAMA_URL = _config['ollama']['OLLAMA_URL']
OLLAMA_MODEL = _config['ollama']['OLLAMA_MODEL']
OLLAMA_TIMEOUT = int(_config['ollama'].get('OLLAMA_TIMEOUT', 60))

# Chat format of pi3 mini models: https://huggingface.co/microsoft/Phi-3-mini-128k-instruct?utm_source=chatgpt.com
def generate_proofread_prompt(user_text):
    prompt = """
    <|system|>
    You are a professional proofreader and writing assistant. You job is to identify the following things in the provided user input:
    • Grammatical errors
    • Spelling mistakes
    • Awkward or unclear phrasing
    • Stylistic improvements

    Guidelines:
    - Do not change the meaning of the sentence.  
    - Do not change the tone of the sentence.  
    - Do not include commentary or explanation.  
    - Output must be a **strict JSON array** with objects containing:  
        - "original": the exact erroneous phrase  
        - "suggested": the improved phrase  
        - "start": 0-based character start index (inclusive)  
        - "end": 0-based character end index (exclusive)  
    <|end|>

    <|user|>
    He go to school everyday. He enjoy to play cricket.
    <|end|>

    <|assistant|>
    [
    {
        "original": "He go",
        "suggested": "He goes",
        "start": 0,
        "end": 6
    },
    {
        "original": "everyday",
        "suggested": "every day",
        "start": 17,
        "end": 25
    },
    {
        "original": "He enjoy to play",
        "suggested": "He enjoys playing",
        "start": 27,
        "end": 45
    }
    ]
    <|end|>

    """

    return prompt + f"""
    <|user|>
    {user_text}
    <|end|>

    <|assistant|>
    """


def generate_modify_prompt(original_text, suggested_text, start, end, user_prompt):
    prompt = """
    <|system|>
    You are a professional proofreader and writing assistant.

    Your task is to rewrite a specific span from a sentence based on the user’s custom instruction.

    Strict Guidelines:
    - Only rewrite the span between the `start` and `end` character indexes (0-based, inclusive/exclusive)
    - Do not change or comment on any other part of the sentence
    - Do not include explanations, lists, or extra content
    - Do not change the tone or meaning unless the instruction explicitly asks for it
    - Output must be a single valid JSON object with this format:
    {
    "new_suggestion": "<your rewritten version of the selected span only>"
    }
    <|end|>

    <|user|>
    original_sentence: "He go to school everyday. He enjoy to play cricket."
    suggested_span: "He enjoys playing"
    start: 27
    end: 45
    user_instruction: "Make it sound more formal"
    <|end|>

    <|assistant|>
    {
    "new_suggestion": "He prefers engaging in cricket"
    }
    <|end|>

    """

    return prompt + f"""
    <|user|>
    original_sentence: "{original_text}"  
    suggested_span: "{suggested_text}"
    start: {start}
    end: {end}
    user_instruction: "{user_prompt}"
    <|end|>

    <|assistant|>
    """

def call_ollama(prompt, system=None):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    if system:
        payload["system"] = system
    response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
    response.raise_for_status()
    return response.json()

# @firebase_auth_required
def proofread():
    """
    Proofread a given text and return suggestions for corrections.
    This endpoint expects a JSON payload with the following field:
    - `text`: The text to be proofread.
    The response will include a JSON array of suggestions, each with:
    - `original`: The exact phrase that needs correction.
    - `suggested`: Your improved version.
    - `start`: Starting index in the original text (0-based).
    - `end`: Ending index in the original text (exclusive).
    """
    data = request.get_json()
    text = data.get('text', '')
    prompt = generate_proofread_prompt(user_text=text)
    try:
        ollama_response = call_ollama(prompt)
        # Try to parse the LLM's response as JSON array
        suggestions = []
        raw = ollama_response.get("response", "[]")
        try:
            suggestions = json.loads(raw)
            if not isinstance(suggestions, list):
                suggestions = []
        except Exception as e:
            logging.error(f"Failed to parse LLM response as JSON array: {e}, raw: {raw}")
            suggestions = []
        return jsonify({
            "original_text": text,
            "suggestions": suggestions
        })
    except Exception as e:
        logging.error(f"Ollama API error: {e}")
        return jsonify({"error": "Failed to get suggestions from LLM."}), 500

@firebase_auth_required
def modify():
    """
    Modify a specific span of text based on user instructions.
    This endpoint expects a JSON payload with the following fields:
    - `original`: The full original text.
    - `suggested`: The current suggestion for the marked text.
    - `start`: The starting character index (0-based, inclusive).
    - `end`: The ending character index (exclusive).
    - `user_prompt`: The user's instruction for how to modify the text.
    The response will include the modified suggestion based on the user's instruction.
    """
    data = request.get_json()
    original = data.get('original', '')
    suggested = data.get('suggested', '')
    start = data.get('start', '')
    end = data.get('end', '')
    user_prompt = data.get('user_prompt', '')
    prompt = generate_modify_prompt(original_text=original, 
                                    suggested_text=suggested,
                                    start=start,
                                    end=end,
                                    user_prompt=user_prompt
                                    )
    try:
        ollama_response = call_ollama(prompt)
        # Try to parse the LLM's response as JSON object
        new_suggestion = None
        raw = ollama_response.get("response", "")
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and "new_suggestion" in parsed:
                new_suggestion = parsed["new_suggestion"]
            else:
                new_suggestion = raw
        except Exception as e:
            logging.error(f"Failed to parse LLM response as JSON object: {e}, raw: {raw}")
            new_suggestion = raw
        return jsonify({
            "original": original,
            "suggested": new_suggestion,
            "user_prompt": user_prompt,
            "start": start,
            "end": end,
            "ollama_response": new_suggestion,
        })
    except Exception as e:
        logging.error(f"Ollama API error: {e}")
        return jsonify({"error": "Failed to get modification from LLM."}), 500
