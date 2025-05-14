from ..base import ChatTutorial
import dachi
import asyncio
import typing

from ..base import OpenAILLM, TextConv


class Tutorial4(ChatTutorial):
    '''Tutorial demonstrating asyncrhonous processing using async_map. 
    The topic will be split up into chunks then the summaries will be summarized.'''

    @property
    def description(self) -> str:
        return '''Tutorial demonstrating asyncrhonous processing using map and reduce'''

    def __init__(self):

        self._dialog = dachi.msg.ListDialog()
        self._model = OpenAILLM(procs=TextConv())
        self._renderer = dachi.msg.FieldRenderer()

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    @dachi.asst.signaturemethod('_model', to_async=True)
    def summarize(self, topic) -> str:
        """Summarize the topic that is shared.

        # Current Topic
        {topic}
        """
        pass

    @dachi.asst.signaturemethod('_model')
    def summarize_summaries(self, cur_summary) -> str:
        """Summarize all of the summaries taht have been shared

        # Current summary
        {cur_summary}
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
            self.summarize,
            dachi.proc.B(dachi.proc.Batched(split_message, size=2, drop_last=False))
        ))
        summary = self.summarize_summaries(
            dachi.inst.render(results)
        )
        yield summary
        
        assistant = dachi.msg.Msg(role='assistant', content=summary)
        self._dialog.append(
            assistant
        )
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
