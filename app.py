from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from pytube import YouTube
from pydub import AudioSegment

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    singer = request.form['singer']
    num_videos = int(request.form['num_videos'])
    audio_duration = int(request.form['audio_duration'])
    email = request.form['email']

    # Perform mashup tasks here (download, convert, merge audio files)
    download_videos(singer, num_videos)
    convert_to_audio()
    cut_audio(audio_duration)
    merge_audios()

    # Dummy implementation for sending email
    send_email(email)

    flash('Mashup generated successfully and sent to your email!', 'success')
    return redirect(url_for('index'))

def download_videos(singer, num_videos):
    search_query = singer + " songs"
    results = YouTube.search(search_query, num_videos)
    for video in results:
        stream = video.streams.filter(only_audio=True).first()
        stream.download(output_path=app.config['UPLOAD_FOLDER'])

def convert_to_audio():
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if file.endswith(".mp4"):
            base = os.path.splitext(file)[0]
            sound = AudioSegment.from_file(os.path.join(app.config['UPLOAD_FOLDER'], file))
            sound.export(os.path.join(app.config['UPLOAD_FOLDER'], f"{base}.mp3"), format="mp3")
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))

def cut_audio(duration):
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if file.endswith(".mp3"):
            sound = AudioSegment.from_file(os.path.join(app.config['UPLOAD_FOLDER'], file))
            cut_sound = sound[:duration*1000]
            cut_sound.export(os.path.join(app.config['UPLOAD_FOLDER'], file), format="mp3")

def merge_audios():
    files = [file for file in os.listdir(app.config['UPLOAD_FOLDER']) if file.endswith(".mp3")]
    combined = AudioSegment.empty()
    for file in files:
        sound = AudioSegment.from_file(os.path.join(app.config['UPLOAD_FOLDER'], file))
        combined += sound
    combined.export(os.path.join(app.config['UPLOAD_FOLDER'], "mashup_audio.mp3"), format="mp3")

def send_email(email):
    # Dummy implementation to send email
    sender_email = "your_email@example.com"
    receiver_email = email
    password = "your_email_password"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Mashup Audio"

    body = "Your mashup audio file is attached."
    msg.attach(MIMEText(body, 'plain'))

    filename = "mashup_audio.mp3"
    attachment = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()

if __name__ == '__main__':
    app.run(debug=True)
