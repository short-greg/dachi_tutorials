from .base import Tutorial
import dachi
import typing
from abc import ABC
import typing
import dachi.adapt.openai


class ChatTutorial(Tutorial):

    def __init__(self):

        self.model = 'gpt-3.5-turbo'
        self.ai = dachi.adapt.openai.OpenAIChatModel('gpt-3.5-turbo')
        self.dialog = dachi.Dialog(messages=[dachi.TextMessage('system', "Respond to the user's question")])

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self.dialog.append(dachi.TextMessage('user', user_message))
        res = ''
        for c in dachi.stream_text(self.dialog.stream_prompt(self.ai)):
            yield c['text']
            res += c['text']
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self.dialog.messages:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
