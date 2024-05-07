
import base64
import os
import uuid
import requests

import streamlit as st
from openai import OpenAI

class Voice:

    def __init__(self, api_key):
        # self.client = OpenAI(api_key=api_key)
        self.key = api_key
        self.path = './chatbot/voice'

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    # def text_to_speech(self, transcript):
    #     response = self.client.audio.speech.create(
    #         model="tts-1-hd",
    #         voice="echo",
    #         input=transcript,
    #     )

    #     unique_filename = str(uuid.uuid4()) + ".mp3"
    #     filepath = os.path.join(self.path, unique_filename)
    #     response.stream_to_file(filepath)

    #     return filepath

    def text_to_speech(self, transcript, voice_id='VR6AewLTigWG4xSOukaG'):
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

        headers = {
            "Accept": "application/json",
            "xi-api-key": self.key
        }

        # Set up the data payload for the API request, including the text and voice settings
        data = {
            "text": transcript,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.9,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        response = requests.post(tts_url, headers=headers, json=data, stream=True)

        unique_filename = str(uuid.uuid4()) + ".mp3"
        filepath = os.path.join(self.path, unique_filename)

        with open(filepath, "wb") as f:
        # Read the response in chunks and write to the file
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        return filepath

    def delete_file(self):
        for file in os.listdir(self.path):
            if file.endswith(".mp3"):
                os.remove(os.path.join(self.path, file))

    def autoplay_audio(self, file_path: str):
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode("utf-8")
        md = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)
