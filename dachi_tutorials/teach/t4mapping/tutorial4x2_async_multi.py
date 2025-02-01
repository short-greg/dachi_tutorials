from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai
from ..base import OpenAILLM



class Tutorial2(ChatTutorial):
    '''Tutorial demonstrating asyncrhonous processing using async_multi. 
    The topic of your message will be summarized and main points listed.'''


    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.ListDialog()

    def clear(self):
        self._dialog = dachi.ListDialog()

    @dachi.ai.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
    def summarize(self, topic) -> str:
        """Summarize the topic that the user presents in his messages

        # User Question
        {topic}
        """
        pass

    @dachi.ai.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
    def list_main_points(self, topic) -> str:
        """List the main points of the topic that the user is requesting in his messages

        # User Question
        {topic}
        """
        pass

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        user_message = dachi.Msg(role='user', content=user_message)
        self._dialog.insert(
            user_message, inplace=True
        )

        topic = dachi.exclude_messages(
            self._dialog, 'system'
        ).render()

        results = dachi.async_multi(
            self.list_main_points.async_forward(topic),
            self.summarize.async_forward(topic)
        )
        message = '\n\n'.join(results)
        yield message
        
        assistant = dachi.Msg(role='assistant', content=response)
        self._dialog.insert(
            assistant, inplace=True
        )
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
