from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai

from ..base import OpenAILLM

class Tutorial1(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial for adding instructions'''
    
    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.ListDialog(
            msg_renderer=dachi.RenderField()
        )
        self._model = OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc())
        self._role = dachi.Cue(
            text=
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

    @dachi.ai.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
    def make_decision(self, question) -> str:
        """
        {instructions}

        """
        instruction = dachi.Cue(
            text="""
            Decide on how to respond to the user. 
            Whether to ask a question, respond directly, probe deeper etc.

            You can choose a combination of these. 
        
            {question}
            """
        )
        instruction = dachi.op.fill(instruction, question=question)
        instruction = dachi.op.cat(
            [self._role, instruction], '\n\n'
        )
        return {
            'instructions': instruction
        }

    @dachi.ai.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
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
