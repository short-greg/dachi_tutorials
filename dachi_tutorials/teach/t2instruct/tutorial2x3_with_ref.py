from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai


class Role(dachi.op.Description):

    descr: str

    def render(self) -> str:
        return f"""
        # Role: {self.name}
        
        {self.descr}
        """

class Tutorial3(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial for adding instructions with a reference.'''

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

    @dachi.signaturefunc(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def make_decision(self, question) -> str:
        """
        {instructions}

        """
        instruction = dachi.Cue(
            text="""
            Decide on how to respond to the user. 
            Whether to ask a question, respond directly, probe deeper etc.

            Refer to {role}

            You can choose a combination of these. 
        
            {question}
            """
        )
        ref = dachi.op.Ref(desc=self._role)
        instruction = dachi.op.fill(instruction, question=question, role=ref)
        instruction = dachi.op.cat(
            [self._role, instruction], '\n\n'
        )
        return {
            'instructions': instruction
        }

    @dachi.signaturefunc(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
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
