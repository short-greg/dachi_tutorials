from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai


class Tutorial1(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial for reading a primitive'''

    def __init__(self):

        self.model = 'gpt-3.5-turbo'
        self._messages = []

    def clear(self):
        self._messages = []

    @dachi.signaturefunc(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def count_vowels(self, text) -> int:
        """Count the number of vowels in the text the user provides

        Output only an integer
        
        # User Text
        {text}
        """
        pass

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._messages.append(dachi.TextMessage('user', user_message))
        # cur_message = self.recommendation(self._messages[-1])

        n_vowels = self.count_vowels(self._messages[-1])
        response = f'Number of vowels: {n_vowels}'
        yield response
        self._messages.append(dachi.TextMessage('assistant', response))
        # self._messages.append(dachi.TextMessage('assistant', cur_message))
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
