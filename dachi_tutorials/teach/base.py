import dachi
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
import streamlit as st


class Option(ABC):

    def __init__(self, name: str):

        self.name = name

    @abstractmethod
    def render(self):
        pass


class Dropdown(Option):

    def __init__(self, name: str, options: typing.List[str], callback=None):
        
        super().__init__(name)
        self.options = options
        self.callback = callback
        self.key = None

    def render(self):

        self.key = f'selected_{self.name}'
        st.selectbox(
            self.name, self.options, 
            on_change=self.callback, 
            key=self.key,
        )
        
    @property
    def selected(self) -> str:
        return st.session_state[self.key]


class Tutorial(ABC):
    
    @abstractmethod
    def forward(self, user_message: str) -> typing.Iterator[str]:
        pass

    def __call__(self, user_message: str) -> typing.Iterator[str]:
        return self.forward(user_message)

    @abstractmethod
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        pass
