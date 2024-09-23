from ..base import Tutorial
import dachi
import typing
from abc import ABC
import typing
import dachi.adapt.openai


class Tutorial1(Tutorial):
    '''First tutorial just using ChatModel
    '''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self.ai = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')
        self._messages = []

    def render_header(self):
        pass

    def clear(self):
        self._messages = []

    def forward(self, user_message: str) -> typing.Iterator[str]:
        user_message = dachi.TextMessage('user', user_message)
        instruction = f"""
        Answer the user's question about movies. Don't talk about anything else

        Question
        {user_message}
        """
        self._messages.append(user_message)

        result = self.ai(dachi.TextMessage('user', instruction))
        yield result.val
        self._messages.append(result.message)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
