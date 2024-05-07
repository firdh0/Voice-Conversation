
import os
import uuid

from openai import OpenAI


class Transcribe:

    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.path = './chatbot/transcribe'

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def speech_to_text(self, audio):
        with open(audio, 'rb') as audio_file:

            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language='id'
            )

        return transcription

    def save_file(self, audio_bytes):
        unique_filename = str(uuid.uuid4()) + ".mp3"
        filepath = os.path.join(self.path, unique_filename)

        with open(filepath,'wb') as f:
            f.write(audio_bytes)

        return filepath

    def delete_file(self):
        for file in os.listdir(self.path):
            if file.endswith(".mp3"):
                os.remove(os.path.join(self.path, file))
