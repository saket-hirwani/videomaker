import logging
from models import VideoContent

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_content(text: str) -> VideoContent:
    """Format user's input text for video creation."""
    try:
        logger.info(f"Processing text input: {text}")

        # Split text into manageable segments (2-3 sentences each)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        sections = []
        current_section = []

        for sentence in sentences:
            current_section.append(sentence)
            if len(current_section) >= 2:
                sections.append({
                    "text": '. '.join(current_section) + '.'
                })
                current_section = []

        # Add any remaining sentences
        if current_section:
            sections.append({
                "text": '. '.join(current_section) + '.'
            })

        # Create video content structure
        content = {
            "title": text[:50] + "..." if len(text) > 50 else text,
            "sections": sections,
            "summary": text[:100] + "..." if len(text) > 100 else text
        }

        logger.info("Successfully formatted content")
        return VideoContent(**content)

    except Exception as e:
        logger.error(f"Error formatting content: {str(e)}", exc_info=True)
        raise Exception(f"Failed to process text: {str(e)}")