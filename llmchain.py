
# from langchain_core.memory import BaseMemory
# from langchain_core.prompts.prompt import PromptTemplate
import streamlit as st
from langchain import LLMChain  # LLM
# from langchain_openai import ChatOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate


# @st.cache_resource
class Langchain:
    def __init__(self, api_key, model_name='gpt-4'):
        self.llm = ChatOpenAI(temperature=0, api_key=api_key, model_name=model_name)
        self.template = """

                        This is OpenAI

                        Previous conversation:
                        {history}

                        Human: {question}

                        Assistant:

                        """
        self.prompt = PromptTemplate(
            input_variables = ["history", "question"],
            template = self.template
        )
        self.memory = ConversationBufferWindowMemory(k=5)
        self.chain = self.create_chain()

    def create_chain(self):
        return LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            verbose=True,
            memory=self.memory
        )

    def chat(self, question):
        response = self.chain.run({"question": question})

        return response
