import json
import datetime
from moviepy.editor import *
import speech_recognition as sr
import whisper
import requests


def clearFolder(*, folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print("failed", e)


def extract_audio_and_save(*, video_file, path_to_save):
    video = VideoFileClip(video_file)
    audio = video.audio
    audio.write_audiofile(os.path.join(path_to_save))


def convert_audio_to_text_and_save(*, audio_file, text_file):
    """
    @Deprecated
    :param audio_file:
    :param text_file:
    :return:
    """
    recognize = sr.Recognizer()
    file = open(os.path.join(text_file), "a")
    with sr.AudioFile(audio_file) as source:
        audio_data = recognize.record(source)
        text = recognize.recognize_google(audio_data)
        file.write(text)
        file.close()


def transcribe_with_whisper(file, text_file):
    model = whisper.load_model("base")
    results = model.transcribe(file)
    print(results)
    file = open(os.path.join(text_file), "w")

    file.write(json.dumps(results, indent=4))
    file.close()


def translate_with_google(q):
    params = {
        "key": "AIzaSyBHhyBEZA2yHlAUtuWjn1CvjRJD5JXLEdo",
        "q": q,
        "target": "es",
        "source": "en"
    }
    response = requests.post(
        'https://translation.googleapis.com/language/translate/v2', params=params)
    return response.json()


def format_timestamp(seconds: float, always_include_hours: bool = False, decimal_marker: str = '.'):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"
