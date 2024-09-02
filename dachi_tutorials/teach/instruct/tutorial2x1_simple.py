from ..base import Tutorial
import dachi
import typing
import dachi.adapt.openai


class Tutorial1(Tutorial):
    '''Tutorial for making it proactive
    '''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.Dialog()
        self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')

        self._instruction = dachi.Instruction(
            "Answer the user's question about movies. Don't talk about anything else."
        )
        self._data = dachi.Instruction(
            """
            # User Question
            {question}
            """
        )

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._dialog.user(
            user_message
        )
        res = ''

        data = dachi.fill(self._data, question=user_message)
        x = dachi.cat([self._instruction, data])
        self._dialog.system(
            x, 0, True
        )
        
        for p1, p2 in self._dialog.stream_prompt(self._model):
            yield p2.val
            res += p2.val
      
        self._messages.assistant(p1.val)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
