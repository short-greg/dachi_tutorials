from ..base import ChatTutorial
import dachi
import typing
import asyncio
import dachi.asst.openai_asst

from ..base import OpenAILLM


class Tutorial5(ChatTutorial):
    '''Tutorial demonstrating asyncrhonous processing using async_map. 
    Each sentence will be summarized and then the summaries will be summarized.'''

    @property
    def description(self) -> str:
        return '''Tutorial demonstrating asyncrhonous sending one to many processes'''

    def __init__(self):

        self._dialog = dachi.msg.ListDialog()
        self._model = OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv())

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    @dachi.asst.signaturemethod('_model', to_async=True)
    def main_points(self, topic) -> str:
        """List up the main points for the topic

        # Current Topic
        {topic}
        """
        pass

    @dachi.asst.signaturemethod('_model', to_async=True)
    def keywords(self, topic) -> str:
        """List up keywords for the topic

        In the format
        keywords: <keyword 1>, ..., <keyword N> 

        # Current Topic
        {topic}
        """
        pass

    @dachi.asst.signaturemethod('_model', to_async=True)
    def abstract(self, topic) -> str:
        """Write up an abstract on the topic

        # Current Topic
        {topic}
        """
        pass

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        split_message = user_message.split('.')
        user_message = dachi.msg.Msg(role='user', content=user_message)
        self._dialog.append(
            user_message
        )

        results = asyncio.run(dachi.proc.async_map(
            [self.main_points, self.keywords, self.abstract],
            dachi.msg.render(split_message)
        ))
        summary = '\n\n'.join(results)

        yield summary
        assistant = dachi.msg.Msg(
            role='assistant', 
            content=summary
        )
        self._dialog.append(
            assistant
        )
    
    def messages(
        self, include: typing.Callable[[str, str], bool]=None
    ) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
