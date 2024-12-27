from flask import Flask, render_template, request, send_file
from gtts import gTTS
import os
from io import BytesIO
from transformers import pipeline  # For summarization

app = Flask(__name__)

# Initialize the summarizer model (using HuggingFace's transformers library)
summarizer = pipeline("summarization")

def generate_audio(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    mp3_fp = BytesIO()
    tts.save(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

def summarize_text(text):
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def explain_text(text):
    # Simple explanation (this can be expanded with AI or predefined rules)
    explanation = "This is an explanation of the text that follows: " + text[:150] + "..."
    return explanation

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    # Read the content of the uploaded file
    text = file.read().decode('utf-8')
    
    # Get the option selected by the user
    option = request.form.get('option', 'narrate')
    
    if option == 'summarize':
        text = summarize_text(text)
    elif option == 'explain':
        text = explain_text(text)
    # For narrate or read out, we just use the original text
    
    # Generate the audio file
    audio_file = generate_audio(text)
    
    # Send the audio file to the user
    return send_file(audio_file, mimetype='audio/mp3', as_attachment=True, download_name="audiobook.mp3")

if __name__ == '__main__':
    app.run(debug=True)