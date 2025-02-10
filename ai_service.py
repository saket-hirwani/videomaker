import os
import json
import requests
from models import VideoContent

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"
MODEL = "google/gemini-2.0-flash-lite-preview-02-05:free"

def generate_content(topic: str) -> VideoContent:
    """Generate video content structure using Google Gemini."""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "Create an educational video script about the given topic. "
                    "Output should be JSON with: title, sections (array of {title, text}), "
                    "and summary."
                },
                {"role": "user", "content": f"Create a video script about: {topic}"}
            ]
        }

        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()

        content = json.loads(response.json()['choices'][0]['message']['content'])
        return VideoContent(**content)

    except Exception as e:
        raise Exception(f"Failed to generate content: {str(e)}")