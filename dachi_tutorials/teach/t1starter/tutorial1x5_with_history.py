from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai


class Tutorial5(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Signature tutorial using history. First it picks movies then recommends'''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.Dialog()
        self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')

    def clear(self):
        self._dialog = dachi.Dialog()

    @dachi.signaturefunc(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def pick_movies(self, question) -> str:
        """List up several movies related to the user's question {question}
        """
        pass

    @dachi.signaturefunc(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
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
        
        self._dialog.add(
            dachi.TextMessage('system', self.recommendation.i(user_message))
        )
        self._dialog.user(
            user_message
        )
        res = ''
        for p1, p2 in self._dialog.stream_prompt(self._model):
            yield p2.val
            res += p2.val
      
        # yield cur_message
        # self._messages.append(dachi.TextMessage('assistant', p1.val))
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
