
import os
import streamlit as st

from streamlit_float import *
from dotenv import load_dotenv
# from google.colab import userdata
from audio_recorder_streamlit import audio_recorder

import llmchain
import transcribe
import voice

load_dotenv()
key = os.getenv("openai_api_key")

transcribe = transcribe.Transcribe(api_key=key)
langchain = llmchain.Langchain(api_key=key)
voice = voice.Voice(api_key=key)

float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Yoii gess"}
        ]

initialize_session_state()

st.title("COBAGESS")

# Create footer container for the microphone
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


if audio_bytes:
    # Write the audio bytes to a file
    with st.spinner("Transcribing..."):

        file_path = transcribe.save_file(audio_bytes)
        transcript = transcribe.speech_to_text(file_path)

        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)

if st.session_state.messages[-1]["role"] != "assistant":

    with st.chat_message("assistant"):
        # contoh_response = 'Hello'
        # st.write(contoh_response)
        with st.spinner("Thinking🤔..."):
            data = st.session_state.messages
            last_user_index = None
            for i, item in enumerate(data):
                if item["role"] == "user":
                    last_user_index = i

            # Mengambil nilai content dari peran "user" terakhir jika ditemukan
            if last_user_index is not None:
                last_user_content = data[last_user_index]["content"]

            response = langchain.chat(last_user_content)

            audio_file = voice.text_to_speech(response)
            voice.autoplay_audio(audio_file)

        st.write(response)
            # st.write(file_path)
        st.session_state.messages.append({"role": "assistant", "content": response})
        voice.delete_file()
        transcribe.delete_file()


# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")
