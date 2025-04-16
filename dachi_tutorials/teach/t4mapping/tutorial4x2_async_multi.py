import asyncio
from ..base import ChatTutorial
import dachi
import typing
import dachi.asst.openai_asst
from ..base import OpenAILLM



class Tutorial2(ChatTutorial):
    '''Tutorial demonstrating asyncrhonous processing using async_multi. 
    The topic of your message will be summarized and main points listed.'''


    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.msg.ListDialog()
        self._renderer = dachi.msg.FieldRenderer()

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    @dachi.asst.signaturemethod(OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv()), to_async=True)
    def summarize(self, topic) -> str:
        """Summarize the topic that the user presents in his messages

        # User Question
        {topic}
        """
        pass

    @dachi.asst.signaturemethod(OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv()), to_async=True)
    def list_main_points(self, topic) -> str:
        """List the main points of the topic that the user is requesting in his messages

        # User Question
        {topic}
        """
        pass

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        user_message = dachi.msg.Msg(role='user', content=user_message)
        self._dialog.append(user_message)

        topic = self._renderer(dachi.msg.exclude_messages(
            self._dialog, 'system'
        ))

        results = asyncio.run(dachi.proc.async_multi(
            self.list_main_points(topic),
            self.summarize(topic)
        ))
        message = '\n\n'.join(results)
        yield message
        
        assistant = dachi.msg.Msg(role='assistant', content=message)
        self._dialog.append(assistant)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
