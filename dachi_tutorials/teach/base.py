import dachi
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
import streamlit as st
import threading
import time
from streamlit.runtime.scriptrunner import add_script_run_ctx
import openai


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
    """A chat tutorial for using Dachi."""

    @property
    def description(self) -> str:
        return self.__doc__
    
    @abstractmethod
    def forward(self, user_message: str) -> typing.Iterator[str]:
        pass

    def __call__(self, user_message: str) -> typing.Iterator[str]:
        return self.forward(user_message)

    @abstractmethod
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        pass


class AgentTutorial(ABC):

    @property
    def description(self) -> str:
        return self.__doc__

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
        t = threading.Thread(target=self._runner, daemon=True)
        add_script_run_ctx(t)
        t.start()

    def stop(self):
        with self._lock:
            self._running = False

    @abstractmethod
    def tick(self) -> typing.Optional[str]:
        pass

    @property
    def running(self):
        return self._running

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


class OpenAILLM(dachi.ai.LLM):

    def __init__(self, model='gpt-4o-mini', resp_procs=[], kwargs: typing.Dict=None):
        kwargs = kwargs or {}
        kwargs['model'] = model
        super().__init__(
            self._forward, self._aforward, 
            self._stream, self._astream,
            resp_procs, 
            kwargs
        )
    
    def _forward(self, messages: typing.List[typing.Dict], **kwargs):
        client = openai.Client()
        res = client.chat.completions.create(
            messages=messages,
            stream=False,
            **kwargs
        )
        return res

    async def _aforward(self, messages: typing.List[typing.Dict], **kwargs):
        client = openai.AsyncClient()
        return await client.chat.completions.create(
            messages=messages,
            stream=False,
            **kwargs
        )

    def _stream(self, messages: typing.List[typing.Dict], **kwargs):
        client = openai.Client()
        for chunk in client.chat.completions.create(
            messages=messages,
            stream=True,
            **kwargs
        ):
            yield chunk

    async def _astream(self, messages: typing.List[typing.Dict], **kwargs):
        client = openai.AsyncClient()
        async for chunk in await client.chat.completions.create(
            messages=messages,
            stream=True,
            **kwargs
        ):
            yield chunk

