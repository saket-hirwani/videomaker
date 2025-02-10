import os
import json
import logging
import requests
from models import VideoContent

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"
MODEL = "google/gemini-2.0-flash-lite-preview-02-05:free"

def generate_content(topic: str) -> VideoContent:
    """Generate video content structure using Google Gemini."""
    try:
        logger.info(f"Generating content for topic: {topic}")

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost:5000",  # Required by OpenRouter
            "X-Title": "AI Video Generator"  # Optional but recommended
        }

        data = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": """Create an educational video script about the given topic. 
                    Format the response as JSON with the following structure:
                    {
                        "title": "Topic Title",
                        "sections": [
                            {
                                "title": "Section Title",
                                "text": "Section Content"
                            }
                        ],
                        "summary": "Brief summary of the topic"
                    }"""
                },
                {"role": "user", "content": f"Create a video script about: {topic}"}
            ]
        }

        logger.debug("Making API request to OpenRouter")
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()

        content = json.loads(response.json()['choices'][0]['message']['content'])
        logger.info("Successfully generated content")
        return VideoContent(**content)

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}", exc_info=True)
        raise Exception(f"Failed to connect to AI service: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse API response: {str(e)}", exc_info=True)
        raise Exception("Failed to parse AI response")
    except Exception as e:
        logger.error(f"Unexpected error in content generation: {str(e)}", exc_info=True)
        raise Exception(f"Failed to generate content: {str(e)}")