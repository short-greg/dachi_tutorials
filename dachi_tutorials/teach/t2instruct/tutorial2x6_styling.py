from ..base import Tutorial
import dachi
import typing
import dachi.adapt.openai
import pydantic


class Role(pydantic.BaseModel):

    name: str
    descr: str

    def render(self) -> str:
        return f"""
        # Role: {self.name}
        
        {self.descr}
        """


class Tutorial6(Tutorial):
    '''Tutorial for adding instructions
    '''
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

    @dachi.instructmethod(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def recommendation(self, question) -> str:
        """
        """
        details = dachi.Instruction(
            text='Recommend a movie based on the users' 
            'message according to the response format.'
        )
        role = dachi.Instruction(text='Role: Recommender')
        header = dachi.section(
            role, details, linebreak=1
        )

        response_format = dachi.section(
            'Response Format', 
            '<Make recommendation or state current understanding>\n'
            '<Ask follow-up question>'
        )
        user_question = dachi.section(
            "Here is the user's question", 
            f'{question}'
        )

        return dachi.cat([header, response_format, user_question])

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
