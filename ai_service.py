import os
import json
import logging
import requests
from models import VideoContent

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = "google/gemini-2.0-flash-lite-preview-02-05:free"

def generate_content(text: str) -> VideoContent:
    """Generate video content structure from user's text input."""
    try:
        logger.info(f"Processing text input: {text}")

        if not API_KEY:
            logger.error("OpenRouter API key not found in environment variables")
            raise Exception("OpenRouter API key not configured. Please set the OPENROUTER_API_KEY environment variable.")

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://replit.com",  # Required by OpenRouter
            "X-Title": "AI Video Generator",  # Optional but recommended
        }

        data = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": """Convert the given text into a video script format.
                    Format the response as JSON with the following structure:
                    {
                        "title": "Brief title based on the content",
                        "sections": [
                            {
                                "text": "A portion of the text optimized for video narration"
                            }
                        ],
                        "summary": "Brief description of the content"
                    }
                    Break the text into natural speaking segments of 2-3 sentences each."""
                },
                {"role": "user", "content": text}
            ]
        }

        logger.debug("Making API request to OpenRouter")
        response = requests.post(API_URL, headers=headers, json=data)

        if response.status_code != 200:
            error_message = f"API request failed with status {response.status_code}"
            try:
                error_details = response.json()
                error_message += f": {error_details.get('error', {}).get('message', response.text)}"
            except:
                error_message += f": {response.text}"
            logger.error(error_message)
            raise Exception(error_message)

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