import dachi
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
import streamlit as st
import threading
import time


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


class ChatTutorial(ABC):
    
    @abstractmethod
    def forward(self, user_message: str) -> typing.Iterator[str]:
        pass

    def __call__(self, user_message: str) -> typing.Iterator[str]:
        return self.forward(user_message)

    @abstractmethod
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        pass


class AgentTutorial(ABC):

    def __init__(self, callback: typing.Callable, interval: float=1./60):

        self._callback = callback
        self._running = False
        self._interval = interval
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
        threading.Thread(target=self._runner, daemon=True).start()

    def stop(self):
        with self._lock:
            self._running = False

    @abstractmethod
    def tick(self) -> typing.Optional[str]:
        pass

    def _runner(self):
        
        while self._running:
            message = self.tick()
            if message is not None:
                self._callback(message)
            time.sleep(self._interval)

    @property
    def callback(self) -> typing.Callable:
        return self._callback

    @abstractmethod
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        pass
