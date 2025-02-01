from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai
import pydantic
from ..base import OpenAILLM


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
        self._dialog = dachi.ListDialog(
            msg_renderer=dachi.RenderField()
        )
        self._model = OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc())
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
        self._dialog = dachi.ListDialog(
            msg_renderer=dachi.RenderField()
        )


    @dachi.ai.instructmethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
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
        
        self._dialog.insert(
            dachi.Msg(role='user', content=user_message), inplace=True
        )
        res = ''
        dialog = dachi.exclude_messages(
            self._dialog, 'system'
        )
        for c in self.recommendation.stream(
            dialog.render()
        ):
            if c is not None:
                yield c
                res += c
      
        self._dialog.insert(
            dachi.Msg(role='assistant', content=res),
            inplace=True
        )
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
