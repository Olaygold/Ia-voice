import os
from flask import Flask, request, send_file
from gtts import gTTS
from io import BytesIO
from transformers import pipeline
from flask_cors import CORS  # Added CORS to handle cross-origin requests

app = Flask(__name__)

# Enable CORS for cross-origin requests (if needed)
CORS(app)

# Initialize the summarizer model
summarizer = pipeline("summarization")

def generate_audio(text, lang='en'):
    """Generate an audio file from text using gTTS."""
    tts = gTTS(text=text, lang=lang)
    mp3_fp = BytesIO()
    tts.save(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

def summarize_text(text):
    """Summarize the input text using a summarizer model."""
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def explain_text(text):
    """Generate a simple explanation for the input text."""
    explanation = "This is an explanation of the text that follows: " + text[:150] + "..."
    return explanation

@app.route('/')
def index():
    """Default route to confirm the app is running."""
    return "App is running!"

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file uploads and process the text."""
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    try:
        text = file.read().decode('utf-8')
    except UnicodeDecodeError:
        return "File could not be decoded. Please upload a valid text file.", 400
    
    # Get the option (narrate, summarize, explain) from the form
    option = request.form.get('option', 'narrate')
    
    if option == 'summarize':
        text = summarize_text(text)
    elif option == 'explain':
        text = explain_text(text)
    
    audio_file = generate_audio(text)
    
    # Send the generated audio file as a response
    return send_file(audio_file, mimetype='audio/mp3', as_attachment=True, download_name="audiobook.mp3")

if __name__ == '__main__':
    # Get the PORT from environment variables for deployment
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
