from ..base import Tutorial
import dachi
import typing
import dachi.adapt.openai


class Tutorial2(Tutorial):
    '''First Signature tutorial
    '''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._messages = []

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def answer_question(self, question) -> str:
        """Answer the user's question about movies. Don't talk about anything else 
        
        {question}
        """
        pass

    def clear(self):
        self._messages = []

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._messages.append(dachi.TextMessage('user', user_message))
        cur_message = self.answer_question(self._messages[-1])
        yield cur_message
        self._messages.append(dachi.TextMessage('assistant', cur_message))
        print(len(self._messages))
    
    def messages(
        self, include: typing.Callable[[str, str], bool]=None
    ) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
