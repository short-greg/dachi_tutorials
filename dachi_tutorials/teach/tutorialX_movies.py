from .base import ChatTutorial
import dachi
import typing
from abc import ABC
import pandas as pd
import os
import opendatasets as od
from .base import Dropdown
import streamlit as st

import typing


# Assign the Kaggle data set URL into variable
# dataset = 'https://www.kaggle.com/ryanholbrook/dl-course-data'
dataset = 'https://www.kaggle.com/datasets/ashpalsingh1525/imdb-movies-dataset'
# Using opendatasets let's download the data sets
od.download(dataset, './data')


class MoviesTutorial(ChatTutorial):

    def __init__(self):

        self.model = 'gpt-3.5-turbo'
        self.dialog = dachi.Dialog()
        self.ai_model = dachi.adapt.OpenAIChatModel(
            self.model, temperature=0.0
        )
        self.dialog.system(
            "Respond to the user's questions about the data provided in the next message."
        )
        #     dachi.adapt.openai.OpenAIChatModel('gpt-3.5-turbo'), 
        #     [dachi.TextMessage('system', "Respond to the user's questions about the data provided in the next message.")]
        # )
        df = pd.read_csv(
            'data/imdb-movies-dataset/imdb_movies.csv'
        )
        self.store = dachi.store.DFStore(df)

    def render_header(self):

        st.text_input(
            'Year', value='2024', key='Movies_Year'
        )
        st.text_input(
            'Director', value='Steven Spielberg', key='Movies_Director'
        )

    def forward(self, user_message: str) -> typing.Iterator[str]:

        director = st.session_state.Movies_Director
        year = st.session_state.Movies_year
        query = self.store.where(
            (dachi.store.Key('Director') == director) &
            (dachi.store.Key('Year') == year)
        ).select(info='overview')
        
        df = query.retrieve()
        overviews = df['overview'].tolist()
        dialog = dachi.Dialog()
        dialog.system(
            str(overviews), _ind=1
        )
        dialog.user(user_message, _ind=1)
        res = ''
        for c in self.dialog.stream_prompt():
            yield c
            res += c
    
    def _messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self.chat.messages:
            if include is None or include(message['role'], message['text']):
                yield message['role'], message['text']
