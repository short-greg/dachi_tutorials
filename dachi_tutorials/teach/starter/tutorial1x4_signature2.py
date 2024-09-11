from ..base import Tutorial
import dachi
import typing
import dachi.adapt.openai


# TEMPLATE
# EXAMPLE

class Tutorial4(Tutorial):
    '''Nested Signature tutorial
    '''

    def __init__(self):

        self.model = 'gpt-3.5-turbo'
        self._messages = []

    def clear(self):
        self._messages = []

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def pick_movies(self, question) -> str:
        """List up several movies related to the user's question {question}
        """
        pass

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def recommendation(self, question) -> str:
        """Answer the user's question about movies. Don't talk about anything else.
        
        # List of possible movies
        {movies}

        # User Question
        {question}
        """
        return {'movies': self.pick_movies(question)}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._messages.append(dachi.TextMessage('user', user_message))
        # cur_message = self.recommendation(self._messages[-1])

        for d, c in self.recommendation.stream_forward(self._messages[-1]):
            yield c
            res += c
        # yield cur_message

        self._messages.append(dachi.TextMessage('assistant', res))
        # self._messages.append(dachi.TextMessage('assistant', cur_message))
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
