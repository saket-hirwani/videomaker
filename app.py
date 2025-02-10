import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import ai_service
import video_generator

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Starting Flask application")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'temp')

# Ensure temp directory exists
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logger.info(f"Temp directory created at {app.config['UPLOAD_FOLDER']}")
except Exception as e:
    logger.error(f"Failed to create temp directory: {str(e)}")
    raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_video():
    try:
        topic = request.form.get('topic')
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400

        logger.info(f"Generating content for topic: {topic}")

        # Generate content using AI
        content = ai_service.generate_content(topic)
        logger.info("Content generated successfully")

        # Generate video
        video_path = video_generator.create_video(content)
        logger.info(f"Video generated at: {video_path}")

        # Return video file
        return send_file(
            video_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f"{secure_filename(topic)}_video.mp4"
        )

    except Exception as e:
        logger.error(f"Error generating video: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/progress')
def get_progress():
    progress = video_generator.get_progress()
    return jsonify({
        'progress': progress['value'],
        'status': progress['status']
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File is too large'}), 413

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Flask development server")
    app.run(host='0.0.0.0', port=5000, debug=True)