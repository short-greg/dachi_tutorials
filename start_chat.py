# from dachi_tutorials.interface import chat

import streamlit as st
import dotenv
import os

from dachi_tutorials.teach.t1starter import (
    tutorial1x0_dummy, tutorial1x1_chat,
    tutorial1x2_signature,
    tutorial1x3_signature_stream,
    tutorial1x4_signature2,
    tutorial1x5_with_history,
    tutorial1x6_proactive, 
    tutorial1x7_use_string_for_model
)

#     tutorial1x6_proactive, tutorial1x7_use_string_for_model,
#     tutorial1x8_use_string_for_model_with_claude,
#     tutorial1x9_use_string_for_model_with_gemini,
#     tutorial1x10_use_string_for_model_with_assistants,
# )
from dachi_tutorials.teach.t2instruct import (
    tutorial2x1_simple, 
    tutorial2x2_with_struct,
    tutorial2x3_with_ref, 
    tutorial2x4_with_glossary,
    tutorial2x5_instructmethod, 
    tutorial2x6_styling
)
from dachi_tutorials.teach.t3read import (
    tutorial3x1_read_primitive, 
    tutorial3x2_read_struct,
    tutorial3x3_read_csv, 
    tutorial3x4_read_kv, 
    tutorial3x5_read_multi,
    tutorial3x7_template
)
from dachi_tutorials.teach.t4mapping import (
    tutorial4x1_async,
    tutorial4x2_async_multi,
    tutorial4x3_iterative_reduce,
    tutorial4x4_map_reduce,
    tutorial4x5_one_to_many
)
from dachi_tutorials.teach.t7_storywriter import (
    tutorial7x1_write_story,
)
from dachi_tutorials.teach.t8_flight_reserver import (
    tutorial8x1_flight_reserver1,
)

dotenv.load_dotenv()
st.title('ChatGPT-like Clone')

tutorial_map = {
    'Tutorial 1-0': tutorial1x0_dummy.Tutorial0,
    'Tutorial 1-1': tutorial1x1_chat.Tutorial1,
    'Tutorial 1-2': tutorial1x2_signature.Tutorial2,
    'Tutorial 1-3': tutorial1x3_signature_stream.Tutorial3,
    'Tutorial 1-4': tutorial1x4_signature2.Tutorial4,
    'Tutorial 1-5': tutorial1x5_with_history.Tutorial5,
    'Tutorial 1-6': tutorial1x6_proactive.Tutorial6,
    'Tutorial 1-7': tutorial1x7_use_string_for_model.Tutorial7,
    # 'Tutorial 1-8': tutorial1x8_use_string_for_model_with_claude.Tutorial8,
    # 'Tutorial 1-9': tutorial1x9_use_string_for_model_with_gemini.Tutorial9,
    # 'Tutorial 1-10': tutorial1x10_use_string_for_model_with_assistants.Tutorial10,
    'Tutorial 2-1': tutorial2x1_simple.Tutorial1,
    'Tutorial 2-2': tutorial2x2_with_struct.Tutorial2,
    'Tutorial 2-3': tutorial2x3_with_ref.Tutorial3,
    'Tutorial 2-4': tutorial2x4_with_glossary.Tutorial4,
    'Tutorial 2-5': tutorial2x5_instructmethod.Tutorial5,
    'Tutorial 2-6': tutorial2x6_styling.Tutorial6,
    'Tutorial 3-1': tutorial3x1_read_primitive.Tutorial1,
    'Tutorial 3-2': tutorial3x2_read_struct.Tutorial2,
    'Tutorial 3-3': tutorial3x3_read_csv.Tutorial3,
    'Tutorial 3-4': tutorial3x4_read_kv.Tutorial4,
    'Tutorial 3-5': tutorial3x5_read_multi.Tutorial5,
    'Tutorial 3-7': tutorial3x7_template.Tutorial7,
    'Tutorial 4-1': tutorial4x1_async.Tutorial1,
    'Tutorial 4-2': tutorial4x2_async_multi.Tutorial2,
    'Tutorial 4-3': tutorial4x3_iterative_reduce.Tutorial3,
    'Tutorial 4-4': tutorial4x4_map_reduce.Tutorial4,
    'Tutorial 4-5': tutorial4x5_one_to_many.Tutorial5,
    'Tutorial 7-1': tutorial7x1_write_story.Tutorial1,
    'Tutorial 8-1': tutorial8x1_flight_reserver1.Tutorial1,
    
}


if 'updated' not in st.session_state:
    st.session_state.updated = False


def write_assistant_message(message):

    st.session_state.updated = True


def change_tutorial():
    if option != st.session_state.current_tutorial:
        st.session_state.tutorial.clear()
        st.session_state.tutorial = tutorial_map[st.session_state.current_tutorial]()
        st.session_state.user_message = None
    print(f'Updated tutorial to {st.session_state.current_tutorial}')


option = st.selectbox(
    'Tutorial', list(tutorial_map.keys()), 
    key='current_tutorial', on_change=change_tutorial
)


if 'tutorial' not in st.session_state:

    st.session_state.tutorial = tutorial1x0_dummy.Tutorial0()

st.text(st.session_state.tutorial.description)

for role, text in st.session_state.tutorial.messages(lambda role, m: role != 'system'):
    with st.chat_message(role):
        st.markdown(text)


if prompt := st.chat_input('What is up?'):
    st.session_state.user_message = prompt
    with st.chat_message('user'):
        st.markdown(prompt)


if 'user_message' in st.session_state and st.session_state.user_message is not None:
    with st.chat_message('assistant'):

        stream = st.session_state.tutorial.forward(
            st.session_state.user_message
        )
        response = st.write_stream(stream)
