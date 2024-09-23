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


class Tutorial2(Tutorial):
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

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def make_decision(self, question) -> str:
        """
        {instructions}

        """
        instruction = dachi.Instruction(
            text="""
            Decide on how to respond to the user. 
            Whether to ask a question, respond directly, probe deeper etc.

            You can choose a combination of these. 
        
            {question}
            """
        )
        instruction = dachi.fill(instruction, question=question)
        instruction = dachi.cat(
            [self._role, instruction], '\n\n'
        )
        return {
            'instructions': instruction
        }

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def recommendation(self, question) -> str:
        """
        {role}
        
        # Respond according to this
        {response}

        # User Question
        {question}
        """
        return {'response': self.make_decision(question), 'role': self._role}

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
