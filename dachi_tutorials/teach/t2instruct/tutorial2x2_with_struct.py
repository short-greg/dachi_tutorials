from ..base import ChatTutorial
import dachi
import typing
import pydantic

import dachi.asst.openai_asst
from ..base import OpenAILLM

class Role(pydantic.BaseModel):

    name: str
    descr: str

    def render(self) -> str:
        return f"""
        # Role: {self.name}
        
        {self.descr}
        """

class Tutorial2(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial for adding instructions'''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.msg.ListDialog()
        self._renderer = dachi.msg.FieldRenderer()
        self._model = OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv())
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
        self._dialog = dachi.msg.ListDialog()

    @dachi.asst.signaturemethod(OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv()))
    def make_decision(self, question) -> str:
        """
        {instructions}

        """
        instruction = dachi.msg.Cue(
            text="""
            Decide on how to respond to the user. 
            Whether to ask a question, respond directly, probe deeper etc.

            You can choose a combination of these. 
        
            {question}
            """
        )
        instruction = dachi.msg.fill(instruction, question=question)
        instruction = dachi.msg.cat(
            [self._role, instruction], '\n\n'
        )
        return {
            'instructions': instruction
        }

    @dachi.asst.signaturemethod(OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv()), to_stream=True)
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
        
        self._dialog.append(
            dachi.msg.Msg(role='user', content=user_message)
        )
        res = ''
        dialog = dachi.msg.exclude_messages(
            self._dialog, 'system'
        )
        for c in self.recommendation(
            self._renderer(dialog)
        ):
            if c is not None:
                yield c
                res += c
      
        self._dialog.append(
            dachi.msg.Msg(role='assistant', content=res)
        )
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
