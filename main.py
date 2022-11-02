import os.path
import pathlib
import subprocess

from flask import Flask, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
from helpers import *
from whisper.utils import write_vtt

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "sooooo_secreeeeetttt_duh"


@app.get('/')
def home():
    return render_template('index.html')


@app.post('/')
def upload():
    if 'file' not in request.files:
        flash("No file Uploaded")
        return redirect(request.url)
    else:
        # clearing a folder
        clearFolder(folder=app.config['UPLOAD_FOLDER'])

        # start uploading the file
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'file.' + file.mimetype.split("/")[1]))

        # extract audio
        extract_audio_and_save(video_file=app.config['UPLOAD_FOLDER'] + '/file.mp4',
                               path_to_save=app.config['UPLOAD_FOLDER'] + '/file.wav')

        transcribe_with_whisper(app.config['UPLOAD_FOLDER'] + '/file.wav', "static/file.json")

        flash("file uploaded")
        return redirect(location="/")


@app.post('/translate')
def translate():
    file = open("static/file.json", "r")
    text = json.loads(file.read())

    print(text)
    # what = []
    # for entry in text:
    #     what.append(entry['text'])

    # translated = translate_with_google(what)

    # print(translated['data']['translations'])
    vtt_file = open('translated.vtt', 'w')

    t = ""
    counter = 0
    for segment in text['segments']:
        # t += f"{entry['time']}\n"
        # t += f"{translated['data']['translations'][counter]['translatedText']} align:middle\n\n"
        # counter = counter + 1
        # print(entry)
        write_vtt(segment, vtt_file)

    # exporttovtt = pathlib.Path('translated.vtt')

    # exporttovtt.write_bytes(t.encode('UTF-8'))




    # subprocess.run([
    #     "ffmpeg",
    #     "-i",
    #     "./static/uploads/file.mp4",
    #     "-i",
    #     "./translated.vtt",
    #     "-map",
    #     "0:v",
    #     "-map",
    #     "0:a",
    #     "-map",
    #     "1",
    #     "-metadata:s:s:0",
    #     "language=[en]",
    #     "-c:v",
    #     "copy",
    #     "-c:a",
    #     "copy",
    #     "-c:s",
    #     "srt",
    #     "out.mp4"
    # ])

    return text


@app.post('/translate-clear')
def translate_clear():
    if os.path.exists("static/file.json"):
        os.unlink("static/file.json")
        return {"message": "ok"}

    return {}


@app.post('/export-to-vtt')
def export_to_vtt():
    data = request.get_data()
    data = json.loads(data)
    vtt = open('translation.vtt', 'w')
    vtt.write(data)
    vtt.close()
    print(data)

    return {}


if __name__ == "__main__":
    app.run(debug=True)
