from queue import Queue
import speech_recognition as sr
from sys import platform
import numpy as np
from datetime import datetime, timedelta
from time import sleep
import os
import requests


def get_transcript(audio_data):
    response = requests.post("https://1ccf-89-187-159-19.ngrok-free.app/transcribe", data=audio_data)
    return response.json()['transcription']
    
def main():
    data_queue = Queue()
    recorder = sr.Recognizer()
    phrase_time = None
    transcription = ['']
    record_timeout = 300  # current limit, then we can adjust to the new limit
    phrase_timeout = 200  # How much time we need to consider for the next phrase
    source = sr.Microphone(sample_rate=16000)
    with source:
        recorder.adjust_for_ambient_noise(source)
        
    # Record the start time
    transcription_start_time = datetime.utcnow()
    def record_callback(_, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        data_queue.put(data)

    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    while True:
        try:
            now = datetime.utcnow()
            if not data_queue.empty():
                phrase_complete = False
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_complete = True
                phrase_time = now
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()
                transcript_text = get_transcript(audio_data)
                if phrase_complete:
                    transcription.append(transcript_text)
                else:
                    transcription[-1] = transcript_text
                os.system('cls' if os.name == 'nt' else 'clear')
                for line in transcription:
                    transcription_end_time = datetime.utcnow()
                    total_transcription_time = transcription_end_time - transcription_start_time
                    print(f"\n\nTotal transcription time: {total_transcription_time}")

                print('', end='', flush=True)
            else:
                sleep(0.25)
        except KeyboardInterrupt:
            # Record the end time when interrupted by the user
         
            break

   
    print("\n\nTranscription:")
    for line in transcription:
        print(line)


if __name__ == "__main__":
    main()
