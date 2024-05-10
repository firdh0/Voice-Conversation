
import math
import os

import streamlit as st
import streamlit.components.v1 as components
# from google.colab import userdata
from audio_recorder_streamlit import audio_recorder
from pydub import AudioSegment
from streamlit_float import *

import icon
import llmchain
import transcribe
import voice

st.set_page_config(page_title="Voice Conversation",
                   page_icon=":bridge_at_night:",
                   layout="wide")
icon.show_icon("📬")
st.title("🔊 Voice Conversation")

if "option" not in st.session_state:
    st.session_state.option = None

def select():
    if st.session_state.option is None:
        st.session_state.option = st.selectbox(
            "Pilih bahasa yang akan digunakan ya!",
            ("Bahasa Inggris", "Bahasa Indonesia"),
            index=None,
            placeholder="Pilih bahasanya...",
            disabled=False
        )
    else:
        st.session_state.option = st.selectbox(
            "Pilih bahasa yang akan digunakan ya!",
            ("Bahasa Inggris", "Bahasa Indonesia"),
            index=None,
            placeholder="Pilih bahasanya...",
            disabled=True
        )

    return st.session_state.option

with st.sidebar:
    
    st.header("Perhatian!")
    st.warning("Sebelum kita mulai Percakapan Suara, yuk pilih bahasanya dan masukkan kunci OpenAI & Sapling yang kamu punya. 😊🔑", icon="🚨")
    st.markdown("Kalau kamu udah masukin kunci OpenAI & Sapling, nanti bakal ada ikon mikrofon. Tiap kali kamu mau ngobrol, tinggal tekan ikon itu ya. Ikonnya bakal berhenti denger otomatis begitu kamu selesai ngomong. 😊🎙️")
    
    st.title("🌐 Bahasa")
    option = select()

    if option is not None:
        st.write("Kamu memilih:", option)

    print(option)

    st.title("🔐 API Key")
    # key = st.text_input('Masukkan kunci OpenAI kamu', type='password')
    key = st.secrets["openai_key"]
    # key3 = st.secrets["elevenlabs_key"]
    key2 = st.text_input('Masukkan kunci Sapling kamu', type='password')

if key.startswith('sk-') and len(key2) == 32:

    float_init()

    def initialize_session_state():
        if "transcribe" not in st.session_state:
            st.session_state.transcribe = transcribe.Transcribe(api_key=key)
        if "langchain" not in st.session_state:
            st.session_state.langchain = llmchain.Langchain(api_key=key)
        if "voice" not in st.session_state:
            st.session_state.voice = voice.Voice(api_key=key)

        if st.session_state.option == 'Bahasa Indonesia':
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "assistant", "content": "😍 Halo! Bagaimana kabarmu hari ini? Ada yang perlu diobrolin?"}
                ]
        else:
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "assistant", "content": "😍 Hello! How are you today? Is there anything you need to discuss?"}
                ]

    initialize_session_state()

    # Create footer container for the microphone
    footer_container = st.container()
    with footer_container:
        audio_bytes = audio_recorder(
            text="Click the following icon",
            recording_color="#ffcc00",
            neutral_color="#aaa9cb",
            icon_size="2x",
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if audio_bytes:
        # Write the audio bytes to a file
        with st.spinner("Transcribing..."):

            if st.session_state.option == 'Bahasa Indonesia':
                language='id'
            else:
                language='en'

            print(f"language: {language}")
        
            file_path = st.session_state.transcribe.save_file(audio_bytes)
            print(file_path)
            transcript = st.session_state.transcribe.speech_to_text(file_path, language)

            audio = AudioSegment.from_file(file_path)
            average_volume = audio.dBFS
            # print("Tipe data dari average_volume:", type(average_volume))
            print(average_volume)

            if math.isinf(average_volume):
                if st.session_state.option == 'Bahasa Indonesia':
                    with st.chat_message("assistant"):
                        st.write('Sepertinya kamu belum berbicara ya?.   Ayo, kita mulai ngobrol! 😉')
                else:
                    with st.chat_message("assistant"):
                        st.write("Looks like you haven't spoken yet, huh? Come on, let's start chatting! 😉")
                
                # st.warning("Looks like you haven't spoken yet, huh? Come on, let's start chatting! 😉")
                
            else:
                if transcript:
                    print(transcript)
                    st.session_state.messages.append({"role": "user", "content": transcript})
                    with st.chat_message("user"):
                        # st.write(transcript)
                        components.html(
                            """
                                <style>
                                #demo-editor {
                                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                                    color: white;
                                }
                                </style>
                                <script src="https://cdn.sapling.ai/sapling-sdk.js"></script>
                                <div contenteditable="true" id="demo-editor" sapling-ignore="true">%s</div>

                                <script type="text/javascript">
                                const key = "%s";

                                Sapling.init({
                                    key: key,
                                    mode: 'dev',
                                    autocomplete: true,
                                    statusBadge: true,
                                    appearance: {
                                        compact: false,
                                        variables: {
                                            acceptText: 'Accept', // extended view only
                                            ignoreText: 'Ignore',
                                        },
                                        customCSS: '',
                                    },
                                });

                                const contentEditable = document.getElementById('demo-editor');
                                Sapling.observe(contentEditable);
                                </script>
                            """ % (transcript, key2),
                        )
                else:
                # Handle empty transcript
                    if st.session_state.option == 'Bahasa Indonesia':
                        with st.chat_message("assistant"):
                            st.write('Sepertinya kamu belum berbicara ya?.   Ayo, kita mulai ngobrol! 😉')
                    else:
                        with st.chat_message("assistant"):
                            st.write("Looks like you haven't spoken yet, huh? Come on, let's start chatting! 😉")
                

    if st.session_state.messages[-1]["role"] != "assistant":

        with st.chat_message("assistant"):

            with st.spinner("Thinking🤔..."):
                data = st.session_state.messages
                last_user_index = None
                for i, item in enumerate(data):
                    if item["role"] == "user":
                        last_user_index = i

                if last_user_index is not None:
                    last_user_content = data[last_user_index]["content"]

                response = st.session_state.langchain.chat(last_user_content)

            with st.spinner("Generating audio response..."):
                audio_file = st.session_state.voice.text_to_speech(response)
                st.session_state.voice.autoplay_audio(audio_file)

            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.voice.delete_file()
            st.session_state.transcribe.delete_file()

    footer_container.float("bottom: 0rem;")
else:
    st.warning('Masukkan dulu kunci OpenAI dan Sapling yang kamu punya ya! 😊🔑', icon='👈')

    
