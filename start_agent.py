# from dachi_tutorials.interface import chat

import streamlit as st
import dotenv
import os


from dachi_tutorials.teach.t5act import (
    tutorial5x0_dummy,
    tutorial5x1_action,
    tutorial5x2_action_sequence,
    tutorial5x3_action_fallback,
    tutorial5x4_action_repeat,
)
from dachi_tutorials.teach.t6act_func import (
    tutorial6x1_action, 
    tutorial6x2_action_sequence,
    tutorial6x3_action_fallback,
    tutorial6x4_action_repeat
)

from dachi_tutorials.teach.t10_train_ridge_regression import (
    tutorial10x1_ridge_regression
) 

from streamlit_autorefresh import st_autorefresh
# from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from streamlit_autorefresh import st_autorefresh

dotenv.load_dotenv()
st.title('AI Agent')

tutorial_map = {
    'Tutorial 5-0': tutorial5x0_dummy.Tutorial0,
    'Tutorial 5-1': tutorial5x1_action.Tutorial1,
    'Tutorial 5-2': tutorial5x2_action_sequence.Tutorial2,
    'Tutorial 5-3': tutorial5x3_action_fallback.Tutorial3,
    'Tutorial 5-4': tutorial5x4_action_repeat.Tutorial4,
    'Tutorial 6-1': tutorial6x1_action.Tutorial1,
    'Tutorial 6-2': tutorial6x2_action_sequence.Tutorial2,
    'Tutorial 6-3': tutorial6x3_action_fallback.Tutorial3,
    'Tutorial 6-4': tutorial6x4_action_repeat.Tutorial4,
    'Tutorial 10-1': tutorial10x1_ridge_regression.Tutorial1,
}


if 'updated' not in st.session_state:
    st.session_state.updated = False

def write_assistant_message(message):

    st.session_state.updated = True


# if 'updated' not in st.session_state:
#     st.session_state.updated = False

if 'update_trigger' not in st.session_state:
    st.session_state.update_trigger = 0


# Callback function to update the messages display
def update_messages(new_message):
    # print('Update messages ', new_message)
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    st.session_state.messages.append(new_message)    
    # st.session_state.update_trigger += 1  # Increment to force re-render
    st.rerun()


def change_tutorial():
    if option != st.session_state.current_tutorial:
        st.session_state.tutorial.clear()
        st.session_state.tutorial = tutorial_map[st.session_state.current_tutorial](update_messages)
    print(f'Updated tutorial to {st.session_state.current_tutorial}')


count = st_autorefresh(interval=1000, limit=100, key="fizzbuzzcounter")

option = st.selectbox(
    'Tutorial', list(tutorial_map.keys()), 
    key='current_tutorial', on_change=change_tutorial
)

if 'tutorial' not in st.session_state:

    st.session_state.tutorial = tutorial5x0_dummy.Tutorial0(update_messages)

st.text(st.session_state.tutorial.description)

st.session_state.update_messages = update_messages

# Start/Stop button logic
tutorial = st.session_state.tutorial
if st.button('Start' if not tutorial.running else 'Stop'):
    if not tutorial.running:
        tutorial.start()
    else:
        tutorial.stop()



for role, text in st.session_state.tutorial.messages(lambda role, m: role != 'system'):
    with st.chat_message(role):
        st.markdown(text)
