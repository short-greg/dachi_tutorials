from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai
from ..base import OpenAILLM


class Tutorial5(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Signature tutorial using history. First it picks movies then recommends'''

    def __init__(self):

        self._dialog = dachi.ListDialog()
        self._model = OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc())

    def clear(self):
        self._dialog = dachi.ListDialog()

    @dachi.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
    def pick_movies(self, question) -> str:
        """List up several movies related to the user's question {question}
        """
        pass

    @dachi.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
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
        
        cue: dachi.Cue = self.recommendation.i(user_message)
        self._dialog.add(
            role='system', content=cue.text,
            _replace=True, ind=0, _inplace=True
        )
        self._dialog.add(
            role='user', content=user_message, _inplace=True
        )

        res = ''
        # TODO: FIX ERROR with it passing a string
        for msg, c in self._model.stream(self._dialog):
            if c is not None:
                yield c
                res += c

        self._dialog.add(
            role='assistant', 
            content=res, 
            _inplace=True
        )

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
