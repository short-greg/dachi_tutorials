import streamlit as st
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import dachi

load_dotenv()

st.title('ChatGPT-like Clone')

client = OpenAI()

def change_tutorial():
    print(f'Updated tutorial to {option}')


option = st.selectbox(
    'Tutorial', ['Tutorial 1', 'Tutorial 2'], on_change=change_tutorial
)

# set up the session
if 'openai_model' not in st.session_state:
    st.session_state['openai_model'] = 'gpt-3.5-turbo'

if 'chat' not in st.session_state:

    st.session_state.chat = dachi.converse.Chat(
        dachi.adapt.openai.OpenAIChatModel('gpt-3.5-turbo'), [dachi.TextMessage('system', "Respond to the user's question")]
    )
    # st.session_state.messages = [{'role': 'system', 'content': system}]


# add the messages
for message in st.session_state.chat.loop(lambda message: message['role'] != 'system'):
    with st.chat_message(message['role']):
        st.markdown(message['text'])

# 
if prompt := st.chat_input('What is up'):

    # st.session_state.messages.append({
    #     'role': 'user', 'content': prompt
    # })
    # if 'user' not in st.session_state:
    st.session_state.user = dachi.TextMessage('user', prompt)

    with st.chat_message('user'):
        st.markdown(prompt)

with st.chat_message('assistant'):
    
    if 'user' in st.session_state:

        stream = st.session_state.chat.stream_text(st.session_state.user)
        response = st.write_stream(stream)
    # stream = client.chat.completions.create(
    #     model=st.session_state['openai_model'],
    #     messages=[
    #         {'role': m['role'], 'content': m['content']}
    #         for m in st.session_state.chat.loop(lambda message: message['role'] != 'system')
    #     ],
    #     stream=True
    # )

# st.session_state.messages.append({
#     'role': 'assistant',
#     'content': response
# })
