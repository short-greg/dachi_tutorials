from ..base import ChatTutorial
import dachi
import typing
import dachi.asst.openai_asst
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

    @dachi.asst.signaturemethod(OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv('content')))
    def pick_movies(self, question) -> str:
        """List up several movies related to the user's question {question}
        """
        pass

    @dachi.asst.signaturemethod(OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv('content')), to_stream=True)
    def recommendation(self, question) -> str:
        """Answer the user's question about movies. Don't talk about anything else.
        
        # List of possible movies
        {movies}

        # User Question
        {question}
        """
        movies = self.pick_movies(question)
        return {'movies': movies}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._messages.append(dachi.msg.Msg(role='user', content=user_message))

        res = ''
        for c in self.recommendation(self._messages[-1]):
            if c is not None:
                yield c
                res += c

        self._messages.append(dachi.msg.Msg(role='assistant', content=res))
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
