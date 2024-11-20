from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai
import pydantic


class Role(dachi.op.Description):

    name: str
    descr: str

    def render(self) -> str:
        return f"""
        # Role: {self.name}
        
        {self.descr}
        """


class Tutorial6(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial for adding instructions with styling'''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.Dialog()
        self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')
        self._role = Role(
            name="Movie Recommender",
            descr=
            """
            You must recommend a movie to the user. 
            Remember you must keep the conversation
            going so you can suggest a movie that will be satisfying to the user.
            """
        )

    def clear(self):
        self._dialog = dachi.Dialog()

    @dachi.instructfunc(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def recommendation(self, question) -> str:
        """
        """
        details = dachi.Cue(
            text='Recommend a movie based on the users' 
            'message according to the response format.'
        )
        role = dachi.Cue(text='Role: Recommender')
        header = dachi.op.section(
            role, details, linebreak=1
        )

        response_format = dachi.op.section(
            'Response Format', 
            '<Make recommendation or state current understanding>\n'
            '<Ask follow-up question>'
        )
        user_question = dachi.op.section(
            "Here is the user's question", 
            f'{question}'
        )

        return dachi.op.cat([header, response_format, user_question])

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._dialog.user(
            user_message
        )
        res = ''
        for p1, p2 in self.recommendation.stream_forward(
            self._dialog.exclude('system').render()
        ):
            yield p2
            res += p2
      
        self._dialog.assistant(p1)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
