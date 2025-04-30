from ..base import ChatTutorial
import dachi
import typing
import dachi.asst.openai_asst
import asyncio

from ..base import OpenAILLM


class Tutorial1(ChatTutorial):
    '''Tutorial demonstrating asyncrhonous processing. 
    The topic of your message will be summarized and main points listed.'''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.msg.ListDialog()
        self._renderer = dachi.msg.FieldRenderer()

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    @dachi.asst.signaturemethod(OpenAILLM(procs=dachi.asst.openai_asst.TextConv()), to_async=True)
    def summarize(self, topic) -> str:
        """Summarize the topic that the user presents in his messages

        If the topic is not clear, then explain so.
        
        # User Question
        {topic}
        """
        pass

    @dachi.asst.signaturemethod(OpenAILLM(procs=dachi.asst.openai_asst.TextConv()), to_async=True)
    def list_main_points(self, topic) -> str:
        """List the main points of the topic that the user is requesting in his messages

        If the topic is not clear, then explain so.
        
        # User Question
        {topic}
        """
        pass

    def render_header(self):
        pass

    async def execute(self, topic: str) -> typing.Tuple[str, str]:

        tasks = []
        async with asyncio.TaskGroup() as tg:
            tasks.append(
                tg.create_task(self.list_main_points(topic))
            )
            tasks.append(
                tg.create_task(self.summarize(topic))
            )
        return tuple(task.result() for task in tasks)

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        user_message = dachi.msg.Msg(role='user', content=user_message)
        self._dialog.append(user_message)

        dialog = dachi.msg.exclude_messages(
            self._dialog, 'system'
        )
        topic = self._renderer(dialog)
        
        response = asyncio.run(self.execute(topic))
        response = f'Main Points: {response[0]}\n\n Summary: {response[1]}'
        yield response
        
        assistant = dachi.msg.Msg(role='assistant', content=response)
        self._dialog.append(assistant)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
