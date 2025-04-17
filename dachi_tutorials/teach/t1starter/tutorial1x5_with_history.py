from ..base import ChatTutorial
import dachi
import typing
import dachi.asst.openai_asst
from ..base import OpenAILLM


class Tutorial5(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Signature tutorial using history. First it picks movies then recommends'''

    def __init__(self):

        self._dialog = dachi.msg.ListDialog()
        self._model = OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv())

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    @dachi.asst.signaturemethod(OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv()))
    def pick_movies(self, question) -> str:
        """List up several movies related to the user's question {question}
        """
        pass

    @dachi.asst.signaturemethod(OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv()))
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
        
        cue: dachi.msg.Cue = self.recommendation.i(user_message)
        self._dialog[0] = (
            dachi.msg.Msg(role='system', content=cue.text)
        )
        self._dialog.append(
            dachi.msg.Msg(role='user', content=user_message)
        )

        res = ''
        # TODO: FIX ERROR with it passing a string
        for msg in self._model.stream(self._dialog):
            c = msg.m['content']
            if c is not None:
                yield c
                res += c

        self._dialog.append(
            msg
        )

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
