
import os

import streamlit as st
import streamlit.components.v1 as components
# from google.colab import userdata
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
from streamlit_float import *

import icon
import llmchain
import transcribe
import voice

# load_dotenv()
# key = os.getenv("openai_api_key")

st.set_page_config(page_title="Voice Conversation",
                   page_icon=":bridge_at_night:",
                   layout="wide")
icon.show_icon("📬")
st.title("🔊 Voice Conversation")

with st.sidebar:
    st.title("🔐 OpenAI API Key")
    key = st.text_input('Input your OpenAI key', type='password')
    key2 = st.text_input('Input your Sapling key', type='password')
    st.header("Attention!")
    st.warning(
        """Before you use Voice Conversation, please enter the OpenAI & Sapling key that you have.""", icon="🚨"
    )
    st.markdown("If you have entered your OpenAI & Sapling key then there will be a microphone icon and please press this icon every time you have a conversation. The icon will stop listening once you have finished speaking")

if not key.startswith('sk-'):
    st.warning('Please input your OpenAI & Sapling key before using!', icon='👈')
else:
    # transcribe = transcribe.Transcribe(api_key=key)
    # langchain = llmchain.Langchain(api_key=key)
    # voice = voice.Voice(api_key=key)

    float_init()

    def initialize_session_state():
        if "transcribe" not in st.session_state:
            st.session_state.transcribe = transcribe.Transcribe(api_key=key)
        if "langchain" not in st.session_state:
            st.session_state.langchain = llmchain.Langchain(api_key=key)
        if "voice" not in st.session_state:
            st.session_state.voice = voice.Voice(api_key=key)

        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "😍 Hello, how are things today? Anything interesting happen?"}
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

            file_path = st.session_state.transcribe.save_file(audio_bytes)
            transcript = st.session_state.transcribe.speech_to_text(file_path)

            if transcript != '':
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
                st.error("Transcript is empty. Please try again with clearer audio.")

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

                if last_user_index is not None:
                    last_user_content = data[last_user_index]["content"]

                response = st.session_state.langchain.chat(last_user_content)

            with st.spinner("Generating audio response..."):
                audio_file = st.session_state.voice.text_to_speech(response)
                # file_path = os.path.normpath(audio_file)
                st.session_state.voice.autoplay_audio(audio_file)

            st.write(response)
                # st.write(file_path)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.voice.delete_file()
            st.session_state.transcribe.delete_file()


    # Float the footer container and provide CSS to target it with
    footer_container.float("bottom: 0rem;")
