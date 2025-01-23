from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai
from ..base import OpenAILLM


# TEMPLATE
# EXAMPLE

class Tutorial4(ChatTutorial):
    """Streaming signature tutorial uses nesting to first pick possible movies before recommending."""

    def __init__(self):

        self.model = 'gpt-3.5-turbo'
        self._messages = []

    def clear(self):
        self._messages = []

    @dachi.ai.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
    def pick_movies(self, question) -> str:
        """List up several movies related to the user's question {question}
        """
        pass

    @dachi.ai.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
    def recommendation(self, question) -> str:
        """Answer the user's question about movies. Don't talk about anything else.
        
        # List of possible movies
        {movies}

        # User Question
        {question}
        """
        movies = self.pick_movies(question)
        print(movies)
        return {'movies': movies}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._messages.append(dachi.Msg(role='user', content=user_message))

        res = ''
        for c in self.recommendation.stream(self._messages[-1]):
            if c is not None:
                yield c
                res += c

        self._messages.append(dachi.Msg(role='assistant', content=res))
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
