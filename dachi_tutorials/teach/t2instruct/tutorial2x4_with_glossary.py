from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai
from ..base import OpenAILLM


class Role(dachi.op.Description):

    descr: str

    def render(self) -> str:
        return f"""
        # Role: {self.name}
        
        {self.descr}
        """

class Tutorial4(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial for adding instructions with a glossary'''

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
        self._glossary = dachi.data.Glossary().add(
            'Sastified', 'The user is satisfied with the recommendation',
        ).add(
            'Dissastified', 'The user is satisfied with the recommendation',
        ).add(
            'Neutral: ', 'The user is neither satisfied nor dissatisfied',
        ).add(
            'Unknown: ', 'It is not known if the user is satisfied',
        )

    def clear(self):
        self._dialog = dachi.ListDialog(
            msg_renderer=dachi.RenderField()
        )

    @dachi.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
    def evaluate_satisfaction(self, conversation) -> str:
        """
        Evaluate whether the user is satisfied with the movie recommendations you've given him 

        # Criteria
        {criteria}
    
        # User conversation
        {conversation}
        """
        return {
            'criteria': self._glossary.render()
        }

    @dachi.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
    def make_decision(self, conversation) -> str:
        """
        {instructions}

        """
        instruction = dachi.Cue(
            text="""

            Decide on how to respond to the user based on your role: {role}. 
            Whether to ask a question, respond directly, probe deeper etc, based on 
            how satisfied the user is.

            You can choose a combination of these. 

            # Satisfaction

            {satisfaction}
        
            # Conversation: 
            
            {conversation}
            """
        )
        ref = dachi.op.Ref(desc=self._role)
        satisfaction = self.evaluate_satisfaction(conversation)
        instruction = dachi.op.fill(
            instruction, conversation=conversation, satisfaction=satisfaction, role=ref
        )
        instruction = dachi.op.cat(
            [self._role, instruction], '\n\n'
        )
        return {
            'instructions': instruction
        }

    @dachi.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
    def recommendation(self, conversation) -> str:
        """
        {role}
        
        # Respond according to this
        {response}

        # Current Conversation
        {conversation}
        """
        return {
            'response': self.make_decision(conversation), 
            'role': self._role
        }

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._dialog.insert(
            dachi.Msg(role='user', content=user_message), 
            inplace=True
        )
        res = ''
        dialog = dachi.exclude_messages(
            self._dialog, 'system'
        )
        for c in self.recommendation.stream(
            dialog.render()
        ):
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
