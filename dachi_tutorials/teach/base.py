import dachi
import typing
from abc import ABC, abstractmethod
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


class OpenAILLM(
    dachi.asst.LLM
):

    def __init__(
        self, model='gpt-4o-mini', 
        procs=[], kwargs: typing.Dict=None
    ):
        
        kwargs = kwargs or {}
        kwargs['model'] = model
        super().__init__(
            procs=procs,
            kwargs=kwargs
        )
    
    def forward(self, messages: typing.List[typing.Dict], **kwargs):
        client = openai.Client()
        return dachi.asst.llm_forward(
            client.chat.completions.create, 
            messages=messages,
            _proc=self.procs,
            **{**self._kwargs, **kwargs}
        )

    async def aforward(self, messages: typing.List[typing.Dict], **kwargs):
        client = openai.AsyncClient()
        return await dachi.asst.llm_aforward(
            client.chat.completions.create, 
            messages=messages,
            _proc=self.procs,
            **{**self._kwargs, **kwargs}
        )

    def stream(self, messages: typing.List[typing.Dict], **kwargs):
        client = openai.Client()
        for msg in dachi.asst.llm_stream(
            client.chat.completions.create, 
            messages=messages,
            _proc=self.procs,
            stream=True,
            **{**self._kwargs, **kwargs}
        ):
            yield msg

    async def astream(self, messages: typing.List[typing.Dict], **kwargs):
        client = openai.AsyncClient()
        async for msg in await dachi.asst.llm_astream(
            client.chat.completions.create, 
            messages=messages,
            _proc=self.procs,
            stream=True,
            **{**self._kwargs, **kwargs}
        ):
            yield msg
