from .base import Tutorial
import dachi
import typing
import dachi.adapt.openai


class SignatureTutorial(Tutorial):

    def __init__(self):

        self.model = 'gpt-3.5-turbo'
        self._messages = []

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-3.5-turbo'))
    def answer_question(self, question) -> str:
        """Answer the user's question {question}
        """
        pass

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._messages.append(dachi.TextMessage('user', user_message))
        cur_message = self.answer_question(self._messages[-1])
        yield cur_message
        self._messages.append(dachi.TextMessage('assistant', cur_message))
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
