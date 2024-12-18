from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai


class Tutorial1(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial for adding instructions'''
    
    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.Dialog()
        self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')
        self._role = dachi.Cue(
            text=
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


# class Tutorial1(Tutorial):
#     '''Tutorial for making it proactive
#     '''

#     def __init__(self):

#         self.model = 'gpt-4o-mini'
#         self._dialog = dachi.Dialog()
#         self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')

#         self._instruction = dachi.Cue(
#             "Answer the user's question about movies. Don't talk about anything else."
#         )
#         self._data = dachi.Cue(
#             """
#             # User Question
#             {question}
#             """
#         )

#     def render_header(self):
#         pass

#     def forward(self, user_message: str) -> typing.Iterator[str]:
        
#         self._dialog.user(
#             user_message
#         )
#         res = ''

#         data = dachi.fill(self._data, question=user_message)
#         x = dachi.cat([self._instruction, data])
#         self._dialog.system(
#             x, 0, True
#         )
        
#         for p1, p2 in self._dialog.stream_prompt(self._model):
#             yield p2.val
#             res += p2.val
      
#         self._messages.assistant(p1.val)
    
#     def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
#         for message in self._dialog:
#             if include is None or include(message['source'], message['text']):
#                 yield message['source'], message['text']


