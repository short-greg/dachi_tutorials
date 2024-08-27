# from dachi_tutorials.interface import chat

import streamlit as st
import dotenv
import os

from dachi_tutorials.teach import tutorial0_dummy, tutorial1_chat

dotenv.load_dotenv()
st.title('ChatGPT-like Clone')


def change_tutorial():
    if option != st.session_state.current_tutorial:
        st.session_state.tutorial = tutorial1_chat.ChatTutorial() if st.session_state.current_tutorial == "Tutorial 1" else tutorial0_dummy.SampleTutorial()
    print(f'Updated tutorial to {st.session_state.current_tutorial}')


option = st.selectbox(
    'Tutorial', ['Tutorial 0', 'Tutorial 1'], 
    key='current_tutorial', on_change=change_tutorial
)

if 'tutorial' not in st.session_state:

    st.session_state.tutorial = tutorial0_dummy.SampleTutorial()


for role, text in st.session_state.tutorial.messages(lambda role, m: role != 'system'):
    with st.chat_message(role):
        st.markdown(text)


if prompt := st.chat_input('What is up?'):
    st.session_state.user_message = prompt
    with st.chat_message('user'):
        st.markdown(prompt)


with st.chat_message('assistant'):
    
    if 'user_message' in st.session_state:
        # import os
        # os.write(1,b'Something was executed.\n')

        stream = st.session_state.tutorial.forward(
            st.session_state.user_message
        )
        response = st.write_stream(stream)


# import streamlit as st
# from openai import OpenAI

# st.title("ChatGPT-like clone")

# # Set OpenAI API key from Streamlit secrets
# client = OpenAI()

# # Set a default model
# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5-turbo"

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Accept user input
# if prompt := st.chat_input("What is up?"):
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         stream = client.chat.completions.create(
#             model=st.session_state["openai_model"],
#             messages=[
#                 {"role": m["role"], "content": m["content"]}
#                 for m in st.session_state.messages
#             ],
#             stream=True,
#         )
#         response = st.write_stream(stream)
#     st.session_state.messages.append({"role": "assistant", "content": response})
