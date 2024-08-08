from .base import Tutorial
import dachi
import typing
from abc import ABC
import typing


class ChatTutorial(Tutorial):

    def __init__(self):

        self.model = 'gpt-3.5-turbo'
        self.chat = dachi.converse.Chat(
            dachi.adapt.openai.OpenAIChatModel('gpt-3.5-turbo'), [dachi.TextMessage('system', "Respond to the user's question")]
        )
        
    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        message = dachi.TextMessage('user', user_message)
        res = ''
        for c in self.chat.stream_text(message):
            yield c
            res += c
    
    def loop(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self.chat.messages:
            print(message)
            if include is None or include(message['role'], message['text']):
                yield message['role'], message['text']
