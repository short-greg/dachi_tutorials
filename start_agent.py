# from dachi_tutorials.interface import chat

import streamlit as st
import dotenv
import os

from dachi_tutorials.teach.t5act import (
    tutorial5x0_dummy,
    tutorial5x1_action,
)

dotenv.load_dotenv()
st.title('ChatGPT-like Clone')

tutorial_map = {
    'Tutorial 5-0': tutorial5x0_dummy.Tutorial0,
    'Tutorial 5-1': tutorial5x1_action.Tutorial1,
    # 'Tutorial 5-2': tutorial5x2_action_streamed.Tutorial2,
}


if 'updated' not in st.session_state:
    st.session_state.updated = False



def write_assistant_message(message):

    st.session_state.updated = True


def change_tutorial():
    if option != st.session_state.current_tutorial:
        st.session_state.tutorial.clear()
        st.session_state.tutorial = tutorial_map[st.session_state.current_tutorial]()
    print(f'Updated tutorial to {st.session_state.current_tutorial}')


option = st.selectbox(
    'Tutorial', list(tutorial_map.keys()), 
    key='current_tutorial', on_change=change_tutorial
)


if 'tutorial' not in st.session_state:

    st.session_state.tutorial = tutorial5x0_dummy.Tutorial0()


for role, text in st.session_state.tutorial.messages(lambda role, m: role != 'system'):
    with st.chat_message(role):
        st.markdown(text)


if prompt := st.chat_input('What is up?'):
    st.session_state.user_message = prompt
    with st.chat_message('user'):
        st.markdown(prompt)


with st.chat_message('assistant'):
    
    if 'user_message' in st.session_state:

        stream = st.session_state.tutorial.forward(
            st.session_state.user_message
        )
        response = st.write_stream(stream)
