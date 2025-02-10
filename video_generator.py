import os
import logging
import tempfile
from models import VideoContent
from moviepy.editor import ColorClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

current_progress = {'value': 0, 'status': 'idle'}

def get_progress():
    return current_progress

def create_video(content: VideoContent):
    try:
        current_progress['status'] = 'starting'
        current_progress['value'] = 0

        clips = []
        temp_files = []

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

                # Create simple background clip
                bg_clip = ColorClip(size=(1280, 720), color=(0, 0, 0))
                video_clip = bg_clip.set_duration(duration).set_audio(audio_clip)
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