from .base import Tutorial
import dachi
import typing
import dachi.adapt.openai


class SignatureTutorial2(Tutorial):

    def __init__(self):

        self.model = 'gpt-3.5-turbo'
        self._messages = []

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-3.5-turbo'))
    def pick_country(self, continent) -> str:
        """Choose a country in this continent {continent}
        """
        pass

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-3.5-turbo'))
    def largest_cities(self, continent) -> str:
        """Output the country name and the two largest cities in the country {country}
        """
        return {'country': self.pick_country(continent)}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._messages.append(dachi.TextMessage('user', user_message))
        cur_message = self.largest_cities(self._messages[-1])
        yield cur_message
        self._messages.append(dachi.TextMessage('assistant', cur_message))
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
