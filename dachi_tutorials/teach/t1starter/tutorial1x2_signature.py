from ..base import ChatTutorial
import dachi
import typing
from ..base import TextConv

from ..base import OpenAILLM


class Tutorial2(ChatTutorial):
    """This tutorial uses a signature method in order to generate movie recommendations.
    It has no history.
    """

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._messages = []

    @dachi.asst.signaturemethod(
        OpenAILLM(procs=[TextConv('content')]), llm_out='content'
    )
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

        self._messages.append(
            dachi.msg.Msg(role='user', content=user_message)
        )
        response = self.answer_question(
            user_message
        )
        self._messages.append(
            dachi.msg.Msg(role='assistant', content=response)
        )
        yield response

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
