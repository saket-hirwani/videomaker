import os
import logging
import tempfile
from models import VideoContent

logger = logging.getLogger(__name__)

# Configure detailed logging for imports
logging.basicConfig(level=logging.DEBUG)
logger.info("Starting video generator module")

try:
    logger.info("Importing moviepy.editor")
    from moviepy.editor import TextClip, ColorClip, concatenate_videoclips, AudioFileClip
    logger.info("Successfully imported moviepy.editor")
except ImportError as e:
    logger.error(f"Failed to import moviepy.editor: {str(e)}")
    raise

try:
    logger.info("Importing gTTS")
    from gtts import gTTS
    logger.info("Successfully imported gTTS")
except ImportError as e:
    logger.error(f"Failed to import gTTS: {str(e)}")
    raise

current_progress = {'value': 0, 'status': 'idle'}

def get_progress():
    return current_progress

def create_video(content: VideoContent):
    try:
        current_progress['status'] = 'starting'
        current_progress['value'] = 0

        clips = []
        temp_files = []  # Track temporary files for cleanup

        # Create title slide
        logger.info("Creating title slide")
        title_clip = TextClip(
            content.title,
            fontsize=70,
            color='white',
            size=(1920, 1080),
            bg_color='black',
            method='caption'
        ).set_duration(5)  # Fixed duration for title
        clips.append(title_clip)

        # Create section clips
        total_sections = len(content.sections)
        for idx, section in enumerate(content.sections):
            try:
                current_progress['value'] = (idx / total_sections) * 100
                current_progress['status'] = f'Processing section {idx + 1}/{total_sections}'
                logger.info(f"Processing section {idx + 1}")

                # Generate text-to-speech
                tts = gTTS(text=section['text'])
                temp_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                temp_files.append(temp_audio.name)
                tts.save(temp_audio.name)

                # Get audio duration
                audio_clip = AudioFileClip(temp_audio.name)
                duration = audio_clip.duration
                audio_clip.close()

                # Create text clip with matching duration
                text_clip = TextClip(
                    section['text'],
                    fontsize=40,
                    color='white',
                    size=(1920, 1080),
                    bg_color='black',
                    method='caption'
                ).set_duration(duration)

                # Add audio to text clip
                video_clip = text_clip.set_audio(AudioFileClip(temp_audio.name))
                clips.append(video_clip)

            except Exception as e:
                logger.error(f"Error processing section {idx + 1}: {str(e)}")
                raise

        # Concatenate all clips
        logger.info("Concatenating clips")
        final_clip = concatenate_videoclips(clips)

        # Export video
        output_path = os.path.join(tempfile.gettempdir(), 'output.mp4')
        logger.info(f"Exporting video to {output_path}")
        final_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac'
        )

        current_progress['status'] = 'complete'
        current_progress['value'] = 100

        # Cleanup
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {temp_file}: {str(e)}")

        return output_path

    except Exception as e:
        current_progress['status'] = 'error'
        logger.error(f"Video generation failed: {str(e)}", exc_info=True)
        raise Exception(f"Failed to generate video: {str(e)}")
    finally:
        # Cleanup in case of error
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass