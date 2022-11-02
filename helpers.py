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

    final = {"final": results["segments"]}

    # final = whisper_segments_to_vtt_data(results["segments"])

    file.write(json.dumps(results, indent=4))
    file.close()


def translate_with_google(q):
    params = {
        "key": "AIzaSyBHhyBEZA2yHlAUtuWjn1CvjRJD5JXLEdo",
        "q": q,
        "target": "ar",
        "source": "en"
    }
    response = requests.post('https://translation.googleapis.com/language/translate/v2', params=params)
    return response.json()


def whisper_segments_to_vtt_data(result_segments):
    """
    This function iterates through all whisper
    segements to format them into WebVTT.
    """
    what = []

    data = ""
    for idx, segment in enumerate(result_segments):
        num = idx + 1
        data += f"{num}\n"
        start_ = datetime.timedelta(seconds=segment.get('start'))
        start_ = timedelta_to_videotime(str(start_))
        end_ = datetime.timedelta(seconds=segment.get('end'))
        end_ = timedelta_to_videotime(str(end_))
        data += f"{start_} --> {end_}\n"
        text = segment.get('text').strip()
        time = f"{start_} --> {end_}"

        what.append({"id": idx+1, "time": time, "text": text})
        data += f"{text}\n\n"
    return what


def timedelta_to_videotime(delta):
    """
    Here's a janky way to format a
    datetime.timedelta to match
    the format of vtt timecodes.
    """
    parts = delta.split(":")
    if len(parts[0]) == 1:
        parts[0] = f"0{parts[0]}"
    new_data = ":".join(parts)
    parts2 = new_data.split(".")
    if len(parts2) == 1:
        parts2.append("000")
    elif len(parts2) == 2:
        parts2[1] = parts2[1][:2]
    final_data = ".".join(parts2)
    return final_data
