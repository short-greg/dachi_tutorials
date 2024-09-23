from ..base import Tutorial
import dachi
import typing
import dachi.adapt.openai


class Role(dachi.Description):

    descr: str

    def render(self) -> str:
        return f"""
        # Role: {self.name}
        
        {self.descr}
        """
    

class Tutorial4(Tutorial):
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
        self._glossary = dachi.Glossary().add(
            'Sastified', 'The user is satisfied with the recommendation',
        ).add(
            'Dissastified', 'The user is satisfied with the recommendation',
        ).add(
            'Neutral: ', 'The user is neither satisfied nor dissatisfied',
        ).add(
            'Unknown: ', 'It is not known if the user is satisfied',
        )

    def clear(self):
        self._dialog = dachi.Dialog()

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
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

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def make_decision(self, conversation) -> str:
        """
        {instructions}

        """
        instruction = dachi.Instruction(
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
        ref = dachi.Ref(desc=self._role)
        satisfaction = self.evaluate_satisfaction(conversation)
        instruction = dachi.fill(
            instruction, conversation=conversation, satisfaction=satisfaction, role=ref
        )
        instruction = dachi.cat(
            [self._role, instruction], '\n\n'
        )
        return {
            'instructions': instruction
        }

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
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
