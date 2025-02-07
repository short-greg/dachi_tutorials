from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai

from ..base import OpenAILLM

class Tutorial3(ChatTutorial):
    """Streaming signature tutorial uses streaming to generate movie recommendations. Has no history."""

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._messages = []

    @dachi.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
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

        self._messages.append(dachi.Msg(role='user', content=user_message))
        res = ''
        for c in self.answer_question.stream(user_message):
            if c is not None:
                yield c
                res += c
        self._messages.append(dachi.Msg(role='assistant', content=res))

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']