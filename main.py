import os.path
import pathlib

from flask import Flask, render_template, request, redirect, flash, send_file, Response
from helpers import *

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "sooooo_secreeeeetttt_duh"


@app.get('/')
def home():
    return render_template('index.html')


@app.post('/')
def upload():
    print(request.files)

    if 'file' not in request.files:
        flash("No file Uploaded")
        return redirect(request.url)
    else:
        clearFolder(folder=app.config['UPLOAD_FOLDER'])

        file = request.files['file']

        if not file:
            flash("No file Uploaded")
            return redirect(request.url)

        file.save(os.path.join(
            app.config['UPLOAD_FOLDER'], 'file.' + file.mimetype.split("/")[1]))

        extract_audio_and_save(video_file=app.config['UPLOAD_FOLDER'] + '/file.mp4',
                               path_to_save=app.config['UPLOAD_FOLDER'] + '/file.wav')

        transcribe_with_whisper(
            app.config['UPLOAD_FOLDER'] + '/file.wav', "static/file.json")

        flash("file uploaded")
        return redirect(location="/")


@app.post('/translate')
def translate():
    file = open("static/file.json", "r")
    fileSegments = json.loads(file.read())

    body = request.get_json()

    segments = body.split('\n\n')

    for index, segment in enumerate(segments):
        segment = segment.split('\n')

        if len(segment) > 1:
            time = segment[0]

            start = time.split(' --> ')[0]
            end = time.split(' --> ')[1]
            text = segment[1]

            fileSegments['segments'][index]['text'] = text
            fileSegments['segments'][index]['start'] = start
            fileSegments['segments'][index]['end'] = end

    writeFile = open("static/file.json", "w")
    writeFile.write(json.dumps(fileSegments))

    translatedText = []
    for entry in fileSegments['segments']:
        translatedText.append(entry['text'])

    print(translatedText)
    translated = translate_with_google(translatedText)

    tanslationFile = open('static/translation.json', 'w')

    translationSegments = []
    for index, entry in enumerate(translated['data']['translations']):
        translationSegments.append({
            "id": index,
            "seek": 0,
            "start": float(fileSegments['segments'][index]['start']),
            "end": float(fileSegments['segments'][index]['end']),
            "text": str(entry['translatedText']),
        })

    tanslationFile.write(json.dumps(translationSegments))
    return {}


@app.post('/translate-clear')
def translate_clear():
    if os.path.exists("static/file.json"):
        os.unlink("static/file.json")
        return {"message": "ok"}

    return {}


@app.get('/export-to-vtt')
def export_to_vtt():
    file = open("static/translation.json", "r")
    text = json.loads(file.read())
    t = "WEBVTT\n"

    for segment in text:
        t += f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n"
        t += f"{segment['text'].strip()}\n\n"

    exporttovtt = pathlib.Path('static/translated.vtt')
    exporttovtt.write_bytes(t.encode('UTF-8'))

    return Response(
        t,
        mimetype="text/vtt",
        headers={"Content-disposition": "attachment; filename=translation.vtt"}
    )


@app.get('/download')
def download():
    return send_file("static/translated.vtt", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
