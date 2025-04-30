from ..base import ChatTutorial
import dachi
import typing
import dachi.asst.openai_asst

from ..base import OpenAILLM


class Tutorial7(ChatTutorial):
    '''Tutorial for making the chatbot proactive. It uses a string to reference the model in signature'''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.msg.ListDialog()
        self._renderer = dachi.msg.FieldRenderer('content')
        self._model = OpenAILLM(procs=dachi.asst.openai_asst.TextConv())

    def clear(self):
        self._dialog = dachi.msg.ListDialog(
            msg_renderer=dachi.msg.RenderMsgField()
        )

    @dachi.asst.signaturemethod(engine='_model')
    def make_decision(self, question) -> str:
        """
        You must recommend a movie to the user. 

        Decide on how to respond to the user. 
        Whether to ask a question, respond directly, probe deeper etc.

        You can choose a combination of these. Remember you must keep the conversation
        going so you can suggest a movie that will be satisfying to the user.

        {question}
        """
        pass

    @dachi.asst.signaturemethod(engine='_model', to_stream=True)
    def recommendation(self, question) -> str:
        """You must recommend a movie to the user.
        
        Remember you must keep the conversation
        going so you can suggest a movie that will be satisfying to the user.
        
        # Respond according to this
        {response}

        # User Question
        {question}
        """
        return {'response': self.make_decision(question)}

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
        for p2 in self.recommendation(
            self._renderer(dialog)
        ):
            if p2 is not None:
                yield p2
                res += p2

        self._dialog.append(
            dachi.msg.Msg(role='assistant', content=res)
        )
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
